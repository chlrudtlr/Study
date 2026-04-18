import os
import shutil
from typing import Any, Dict, List, Optional, TypedDict

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph


class State(TypedDict):
    question: str
    generation: str
    data: str
    sources: List[Dict[str, Any]]
    route: str


class DocumentChatbot:
    def __init__(
        self,
        documents_dir: Optional[str] = None,
        documents_desc: Optional[str] = None,
        force_reload: bool = True,  # 처음 1회만 True, 이후에는 False 권장
    ) -> None:
        self.llm = ChatOllama(model="gemma3:1b")
        self.route_llm = ChatOllama(model="gemma3:1b", format="json")
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

        self.documents_dir = documents_dir
        self.documents_desc = documents_desc or "NVMe Base Specification 문서"

        if documents_dir is not None:
            faiss_dir = documents_dir + "_faiss"

            if os.path.exists(faiss_dir) and not force_reload:
                print("📦 기존 FAISS 인덱스를 로드합니다...")
                self.vectorstore = FAISS.load_local(
                    faiss_dir,
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                print("✅ 기존 FAISS 인덱스 로드 완료")
            else:
                print("📄 문서 로드 및 청크 분할 시작")
                docs = self._load_and_split_documents(documents_dir)
                print(f"✅ 문서 분할 완료 - 총 chunk 수: {len(docs)}")

                print("🧠 임베딩 생성 및 FAISS 인덱스 생성 시작")

                texts = [doc.page_content for doc in docs]
                metadatas = [doc.metadata for doc in docs]

                embeddings: List[List[float]] = []
                total = len(texts)
                batch_size = 10  # 기존 50 -> 10으로 줄이기

                for i in range(0, total, batch_size):
                    batch = texts[i : i + batch_size]
                    start_idx = i + 1
                    end_idx = i + len(batch)

                    print(f"🚀 임베딩 요청 시작: {start_idx}~{end_idx}/{total}")

                    batch_emb = self.embeddings.embed_documents(batch)

                    print(f"✅ 임베딩 요청 완료: {start_idx}~{end_idx}/{total}")

                    embeddings.extend(batch_emb)

                    percent = (end_idx / total) * 100
                    print(f"⏳ 임베딩 진행률: {end_idx}/{total} ({percent:.1f}%)")

                print("📦 FAISS 인덱스 생성 중...")

                text_embeddings = list(zip(texts, embeddings))

                self.vectorstore = FAISS.from_embeddings(
                    text_embeddings=text_embeddings,
                    embedding=self.embeddings,
                    metadatas=metadatas,
                )

                print("✅ FAISS 인덱스 생성 완료")

                if os.path.exists(faiss_dir):
                    shutil.rmtree(faiss_dir)

                print("💾 FAISS 인덱스 저장 시작")
                self.vectorstore.save_local(faiss_dir)
                print("✅ FAISS 인덱스 저장 완료")

            print("🔎 Retriever 생성 시작")
            self.db_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            print("✅ Retriever 생성 완료")

        builder = StateGraph(State)

        builder.add_node("init_answer", self.route_question)
        builder.add_node("rag", self.retrieval)
        builder.add_node("plain_answer", self.answer)
        builder.add_node("answer_with_retrieval", self.answer_with_retrieved_data)

        builder.set_entry_point("init_answer")

        builder.add_conditional_edges(
            "init_answer",
            self._extract_route,
            {
                "rag": "rag",
                "plain_answer": "plain_answer",
            },
        )

        builder.add_conditional_edges(
            "rag",
            self._judge_relevance,
            {
                "Relevant": "answer_with_retrieval",
                "Irrelevant": "plain_answer",
            },
        )

        builder.add_edge("answer_with_retrieval", END)
        builder.add_edge("plain_answer", END)

        self.graph = builder.compile()

    def _load_and_split_documents(self, documents_dir: str) -> List[Document]:
        all_docs: List[Document] = []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""],
        )

        for file in os.listdir(documents_dir):
            if not file.endswith(".pdf"):
                continue

            file_path = os.path.join(documents_dir, file)
            loader = PyPDFLoader(file_path)

            print(f"\n📄 파일 로딩 시작: {file}")

            raw_docs = loader.load()
            total_pages = len(raw_docs)

            print(f"📄 총 페이지 수: {total_pages}")

            processed_pages = 0
            split_docs: List[Document] = []

            for doc in raw_docs:
                doc.metadata["source"] = file
                if "page" in doc.metadata:
                    doc.metadata["page"] = doc.metadata["page"] + 1

                chunks = splitter.split_documents([doc])
                split_docs.extend(chunks)

                processed_pages += 1

                if processed_pages % 10 == 0 or processed_pages == total_pages:
                    percent = (processed_pages / total_pages) * 100
                    print(
                        f"⏳ 페이지 진행률: {processed_pages}/{total_pages} "
                        f"({percent:.1f}%)"
                    )

            print(f"✅ 파일 완료: {file} (총 {total_pages} 페이지 처리)")

            all_docs.extend(split_docs)

        print(f"\n🎉 전체 문서 처리 완료! 총 chunk 수: {len(all_docs)}\n")

        return all_docs

    def invoke(self, question: str) -> Dict[str, Any]:
        answer = self.graph.invoke({"question": question})  # type: ignore
        print("===생성 종료===")
        return answer

    def route_question(self, state: State):
        question = state["question"]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 사용자의 질문이 NVMe Base Specification 문서에서 답할 수 있는지 판단하는 라우터입니다. "
                    f"문서 DB는 {self.documents_desc} 관련 내용입니다. "
                    "질문이 NVMe 명령어, 레지스터, 구조, 스펙 정의, 필드 의미, 동작 방식, 규격 해석과 관련 있으면 rag를 선택하세요. "
                    "문서와 직접 관련 없는 일반 상식, 문서 밖의 내용, 너무 광범위하거나 추상적인 질문이면 plain_answer를 선택하세요. "
                    "반드시 JSON 형식으로만 답하고 "
                    '{"route": "rag"} 또는 {"route": "plain_answer"} 중 하나만 반환하세요.'
                ),
                ("human", "{question}"),
            ]
        )

        chain = prompt | self.route_llm | JsonOutputParser()

        try:
            result = chain.invoke({"question": question})
            route = result["route"].strip().lower()
            if route not in ["rag", "plain_answer"]:
                route = "rag"
        except Exception:
            route = "rag"

        return {
            "question": question,
            "generation": "",
            "data": "",
            "sources": [],
            "route": route,
        }

    def retrieval(self, state: State):
        question = state["question"]
        docs = self.db_retriever.invoke(question)

        context_parts = []
        sources = []

        for doc in docs:
            page = doc.metadata.get("page", "N/A")
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content.strip()

            context_parts.append(f"[Source: {source}, Page: {page}]\n{content}")
            sources.append({"source": source, "page": page})

        return {
            "question": question,
            "generation": "",
            "data": "\n\n".join(context_parts),
            "sources": self._unique_sources(sources),
            "route": "rag",
        }

    def answer(self, state: State):
        question = state["question"]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 한국어로 답변하는 NVMe 도우미입니다. "
                    "먼저 '문서에서 직접 확인되지 않는 내용입니다.'라고 분명히 말한 뒤, "
                    "일반적인 지식을 바탕으로 한국어로 설명하세요. "
                    "확실하지 않은 내용은 단정하지 말고, 추정 또는 일반적 설명임을 드러내세요."
                ),
                ("human", "{question}"),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        generation = chain.invoke({"question": question})

        return {
            "question": question,
            "generation": generation,
            "data": "",
            "sources": [],
            "route": "plain_answer",
        }

    def answer_with_retrieved_data(self, state: State):
        question = state["question"]
        context = state["data"]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 NVMe Base Specification 문서를 기반으로 답변하는 한국어 챗봇입니다. "
                    "반드시 제공된 문맥(context)에 근거해서 답하세요. "
                    "질문에 대한 답을 문서에서 직접 확인할 수 있으면 한국어로 정확하고 이해하기 쉽게 설명하세요. "
                    "영문 원문을 짧게 인용해야 할 필요가 있을 때만 일부 영어를 사용할 수 있습니다. "
                    "문맥에 없는 내용을 지어내지 마세요. "
                    "출처 표시는 시스템이 따로 처리하므로 본문 끝에 페이지 번호를 따로 나열하지 마세요."
                ),
                ("human", "질문:\n{question}\n\n참고 문맥:\n{context}"),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        generation = chain.invoke({"question": question, "context": context})

        return {
            "question": question,
            "generation": generation,
            "data": context,
            "sources": state.get("sources", []),
            "route": "rag",
        }

    def _judge_relevance(self, state: State) -> str:
        data = state.get("data", "").strip()
        if not data:
            return "Irrelevant"

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 질문과 참고 문서의 관련성을 판별하는 전문가입니다. "
                    "문서가 질문에 답하는 데 충분히 관련 있으면 yes, 아니면 no를 반환하세요. "
                    '반드시 JSON 형식으로만 답하고 {"is_relevant": "yes"} 또는 {"is_relevant": "no"} 만 반환하세요.'
                ),
                ("human", "질문:\n{question}\n\n문서:\n{documents}"),
            ]
        )

        chain = prompt | self.route_llm | JsonOutputParser()

        try:
            result = chain.invoke(
                {
                    "question": state["question"],
                    "documents": data,
                }
            )
            return "Relevant" if result["is_relevant"] == "yes" else "Irrelevant"
        except Exception:
            return "Irrelevant"

    def _extract_route(self, state: State) -> str:
        return state["route"]

    def _unique_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique = []

        for src in sources:
            key = (src.get("source"), src.get("page"))
            if key not in seen:
                seen.add(key)
                unique.append(src)

        return unique
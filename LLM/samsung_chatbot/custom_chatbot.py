import os
from typing import List, Optional, TypedDict

import pandas as pd
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import END, StateGraph
from utils import *


class State(TypedDict):
    # 그래프 상태의 속성을 정의합니다.
    # 질문, LLM이 생성한 텍스트, 데이터, 코드를 저장합니다.
    question: str
    generation: str
    # 코드를 여러번 실행할 수 있도록, 생성한 코드와 결과를 저장하는 변수를 str형에서 List[str] 형으로 변경합니다.
    data: List[str]
    code: List[str]


class DocumentChatbot:
    def __init__(
        self,
        documents_dir: Optional[str] = None,
        documents_desc: Optional[str] = None,
        force_reload: bool = False,
    ) -> None:
        """
        Chatbot을 초기화합니다.

        Args:
            documents_dir (Optional[str], optional): 문서 디렉토리 경로. Defaults to None.
            documents_desc (Optional[str], optional): 문서 설명. Defaults to None.
        """
        # [지시사항 0] 여러분이 앞서 실습에서 발급 받은 Tavily Search API Key를 입력합니다.
        os.environ["TAVILY_API_KEY"] = "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"

        # self.llm = ChatOllama(model="mistral:7b")
        # self.route_llm = ChatOllama(model="mistral:7b", format="json")
        # self.embeddings = OllamaEmbeddings(model="mistral:7b")

        self.llm = ChatOllama(model="gemma3:1b")
        self.route_llm = ChatOllama(model="gemma3:1b", format="json")
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

        self.hallucination_count = 0
        self.hallucination_limit = 3

        # PDF 데이터를 불러옵니다.
        if documents_dir is not None:
            self.documents_dir = documents_dir
            self.documents_desc = documents_desc
            if self.documents_desc is None:
                raise ValueError("Please provide a description for the Documents.")
            if os.path.exists(documents_dir + "_faiss") and not force_reload:
                self.vectorstore = FAISS.load_local(
                    documents_dir + "_faiss",
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            else:
                all_pages = []
                for file in os.listdir(documents_dir):
                    if file.endswith(".pdf"):
                        loader = PyPDFLoader(os.path.join(documents_dir, file))
                        docs = loader.load()
                        all_pages.extend(docs)
                        del loader
                self.vectorstore = FAISS.from_documents(
                    all_pages, embedding=self.embeddings
                )
                if os.path.exists(documents_dir + "_faiss"):
                    shutil.rmtree(documents_dir + "_faiss")
                self.vectorstore.save_local(documents_dir + "_faiss")
            self.db_retriever = self.vectorstore.as_retriever()

        # Tavily Web Search Tool을 초기화합니다.
        self.tavily_search_tool = TavilySearchResults(max_results=5)
        # 그래프를 초기화합니다.
        self.graph = StateGraph(State)

        ## 그래프 구성

        # 앞서 정의한 Node를 모두 추가합니다.
        self.graph.add_node("init_answer", self.route_question)

        self.graph.add_node("rag", self.retrieval)
        self.graph.add_node("web_search", self.web_search)

        self.graph.add_node("plain_answer", self.answer)
        self.graph.add_node("answer_with_retrieval", self.answer_with_retrieved_data)

        # 시작지점을 정의합니다.
        self.graph.set_entry_point("init_answer")

        # 간선을 정의합니다.
        # END는 종결 지점을 의미합니다.
        self.graph.add_edge(
            "plain_answer", END
        )  # self.graph.set_finish_point("plain_answer")와 동일합니다.

        # 조건부 간선을 정의합니다.
        # init_answer 노드의 답변을 바탕으로 decide_query 함수에서 query 또는 answer로 분기합니다.
        self.graph.add_conditional_edges(
            "init_answer",
            self._extract_route,
            # 어떤 노드로 이동할지 mapping합니다.
            {
                "web_search": "web_search",
                "rag": "rag",
            },
        )

        # [지시사항 2-A] Retrieve한 문서가 관련이 없는 것 같다면, 웹 검색을 통해 다른 정보를 수집하도록 로직을 수정하세요.
        # Hint. self._judge_relenvance() 메서드를 활용합니다.
        # 이 메서드는 문서가 관련이 있다면 "Relevant", 아니라면 "Irrelevant"를 반환합니다.
        self.graph.add_conditional_edges(
            "rag",
            self._judge_relenvance,
            {"Relevant": "answer_with_retrieval", "Irrelevant": "web_search"},
        )

        # [지시사항 2-B] 웹 검색을 통해 수집한 문서도 관련이 없는 것 같다면, 문서 없이 답변을 생성하도록 로직을 수정하세요.
        # Hint. self._judge_relenvance() 메서드를 동일하게 활용합니다.
        # 이 메서드는 문서가 관련이 있다면 "Relevant", 아니라면 "Irrelevant"를 반환합니다.
        self.graph.add_conditional_edges(
            "web_search",
            self._judge_relenvance,
            {"Relevant": "answer_with_retrieval", "Irrelevant": "plain_answer"},
        )

        # 생성된 답변이 할루시네이션이 의심된다면, 답변을 다시 생성하도록 하는 조건부 간선입니다.
        self.graph.add_conditional_edges(
            "answer_with_retrieval",
            self._judge_hallucination,
            {
                "Relevant": END,
                "Irrelevant": "answer_with_retrieval",
                "No Data": "plain_answer",
            },
        )

        self.graph = self.graph.compile()

    def invoke(self, question) -> str:
        self.hallucination_count = 0
        answer = self.graph.invoke({"question": question})
        print("===생성 종료===")

        return answer

    def answer(self, state: State):
        """
        답변을 바로 생성합니다.

        Args:
            state (dict): 현재 그래프 상태

        Returns:
            state (dict): LLM의 답변을 포함한 새로운 State
        """
        print("---답변 생성---")  # 현재 상태를 확인하기 위한 Print문
        question = state["question"]

        return {
            "question": question,
            "generation": self.llm.invoke(question).content,
            "data": [],
            "code": [],
        }

    def retrieval(self, state: State):
        """
        데이터 검색을 수행합니다.

        Args:
            state (dict): 현재 그래프 상태

        Returns:
            state (dict): 검색된 데이터를 포함한 새로운 State
        """

        def get_retrieved_text(docs):
            result = "\n".join([doc.page_content for doc in docs])
            return result

        print("---데이터 검색---")  # 현재 상태를 확인하기 위한 Print문
        question = state["question"]

        # Retrieval Chain
        retrieval_chain = self.db_retriever | get_retrieved_text

        data = retrieval_chain.invoke(question)

        return {
            "question": question,
            "data": data,
            "generation": None,
            "code": [],
        }

    def web_search(self, state: State):
        """
        웹 검색을 수행합니다.

        Args:
            state (dict): 현재 그래프 상태

        Returns:
            state (dict): 검색된 데이터를 포함한 새로운 State
        """
        print("---웹 검색---")  # 현재 상태를 확인하기 위한 Print문

        query = state["question"]

        results = self.tavily_search_tool.invoke({"query": query})

        data = "\n".join([result["content"] for result in results])

        return {
            "question": query,
            "data": data,
            "generation": None,
            "code": [],
        }

    def answer_with_retrieved_data(self, state: State):
        """
        검색된 데이터를 바탕으로 답변을 생성합니다.

        Args:
            state (dict): 현재 그래프 상태

        Returns:
            state (dict): LLM의 답변을 포함한 새로운 State
        """
        # role에는 "AI 어시스턴트"가, question에는 "당신을 소개해주세요."가 들어갈 수 있습니다.

        print(
            "---검색된 데이터를 바탕으로 답변 생성---"
        )  # 현재 상태를 확인하기 위한 Print문

        question = state["question"]
        data = state["data"]

        # 2챕터의 프롬프트와 체인을 활용합니다.
        messages_with_contexts = [
            (
                "system",
                "당신은 친절한 지원 챗봇입니다. 사용자가 입력하는 정보를 바탕으로 질문에 답하세요.",
            ),
            ("human", "정보: {context}.\n{question}."),
        ]
        prompt_with_context = ChatPromptTemplate.from_messages(messages_with_contexts)

        # 체인 구성
        qa_chain = prompt_with_context | self.llm | StrOutputParser()

        generation = qa_chain.invoke({"context": data, "question": question})
        return {
            "question": question,
            "data": data,
            "generation": generation,
            "code": [],
        }

    def _judge_relenvance(self, state: State) -> str:
        """
        문서와 질문의 관련성을 평가합니다.
        문서와 질문이 관련이 있다면 "Relevant"를 리턴하고, 그렇지 않다면 "Irrelevant"를 리턴합니다.
        Args:
            state (dict): 현재 그래프 상태

        Returns:
            str: 문서와 질문의 관련성이 있다면 "Relevant"를 리턴하고, 그렇지 않다면 "Irrelevant"를 리턴합니다.
        """
        print("---관련성 판단---")
        system_message = (
            "당신은 사용자의 질문과 근거 문서의 관련성을 평가하는 전문가입니다. \n"
            "다음은 주어진 근거 문서입니다: {documents}\n"
            "사용자의 질문과 근거 문서의 관련성을 판단하여 'yes', 'no' 중 하나로 판단하세요. \n"
            "판단 결과를 `is_relevant` key에 저장한 JSON dictionary 형태로 답변하고, 다른 텍스트나 설명을 추가하지 마세요."
        )
        user_message = "질문: {question}"
        relevance_judge_prompt = ChatPromptTemplate.from_messages(
            [("system", system_message), ("human", user_message)]
        )

        relevance_judge_chain = (
            relevance_judge_prompt | self.route_llm | JsonOutputParser()
        )
        try:
            relevance_judge_result = relevance_judge_chain.invoke(
                {
                    "documents": state["data"],
                    "question": state["question"],
                }
            )["is_relevant"]
        except Exception as e:
            print(e)
            relevance_judge_result = "Irrelevant"

        relevance_judge_result = (
            "Relevant" if relevance_judge_result == "yes" else "Irrelevant"
        )

        return relevance_judge_result

    def _judge_hallucination(self, state: State) -> str:
        """
        문서의 관련성을 평가하고, 문서를 바탕으로 할루시네이션 여부를 평가합니다.
        할루시네이션일 경우 "Irrelevant"를 리턴하고, 그렇지 않다면 "Relevant"를 리턴합니다.
        만약 정해진 횟수 이상으로 연속으로 할루시네이션 판단이 나오면 "No Data"를 리턴합니다.
        Args:
            state (dict): 현재 그래프 상태

        Returns:
            str: 답변의 할루시네이션이 아니라면 "Relevant"를 리턴하고, 할루시네이션일 가능성이 높다면 "Irrelevant"를 리턴합니다.
        """
        print("---할루시네이션 판단---")

        # 할루시네이션 판단을 위한 시스템 프롬프트입니다.
        system_message = (
            "당신은 주어진 답변이 근거 문서에 근거를 두는지 여부를 판단하는 전문가입니다. \n"
            "다음은 주어진 근거 문서입니다: {documents}\n"
            "주어진 답변이 근거를 기반으로 하는지 여부를 'yes', 'no' 중 하나로 판단하세요. \n"
            "판단 결과를 `is_relevant` key에 저장한 JSON dictionary 형태로 답변하고, 다른 텍스트나 설명을 추가하지 마세요."
        )
        user_message = "답변: {answer}"
        hallucination_judge_prompt = ChatPromptTemplate.from_messages(
            [("system", system_message), ("human", user_message)]
        )

        hallucination_judge_chain = (  # 체인을 구성합니다.
            hallucination_judge_prompt | self.route_llm | JsonOutputParser()
        )

        # 할루시네이션 여부를 판단합니다.
        try:
            hallucination_judge_result = hallucination_judge_chain.invoke(
                {
                    "documents": state["data"],
                    "answer": state["generation"],
                }
            )["is_relevant"]
        except Exception as e:
            print(e)
            hallucination_judge_result = "Irrelevant"

        hallucination_judge_result = (
            "Relevant" if hallucination_judge_result == "yes" else "Irrelevant"
        )

        if hallucination_judge_result == "Irrelevant":
            self.hallucination_count += 1
            if self.hallucination_count >= self.hallucination_limit:
                hallucination_judge_result = "No Data"

        return hallucination_judge_result

    def route_question(self, state: State):
        """
        질문을 라우팅합니다.

        Args:
            state (dict): 현재 그래프 상태

        Returns:
            state (dict): 라우팅된 질문을 포함한 새로운 State
        """
        print("---질문 라우팅---")

        # [지시사항 1] 사용자의 질문이 저장된 DB와 관련 있는지 판단하기 위한 시스템 프롬프트를 작성하세요.
        # Hint. Tips! 에 작성한 이전 실습의 시스템 프롬프트를 참고하세요.
        # Hint 2. documents의 특징은 self.documents_desc에 저장되어 있습니다.
        #################################################
        route_system_message = (
            "당신은 사용자의 질문에 대해 저장된 문서 DB를 사용할지, 웹 검색을 사용할지 결정하는 전문가입니다. \n"
            f"저장된 문서 DB는 {self.documents_desc}와 관련된 내용을 담고 있습니다. \n"
            f"사용자의 질문이 {self.documents_desc}와 관련된 질문이라면 `rag`를 선택하세요. \n"
            "사용자의 질문이 저장된 문서와 관련이 없거나, 최신 정보 또는 일반적인 웹 정보가 더 적절하다면 `web_search`를 선택하세요. \n"
            "반드시 `rag` 또는 `web_search` 중 하나만 선택하세요. \n"
            "답변은 `route` key 하나만 있는 JSON 형태로 작성하고, 다른 설명은 절대 추가하지 마세요."
        )
        #################################################
        route_user_message = "{question}"
        route_prompt = ChatPromptTemplate.from_messages(
            [("system", route_system_message), ("human", route_user_message)]
        )

        router_chain = route_prompt | self.route_llm | JsonOutputParser()
        route = router_chain.invoke({"question": state["question"]})["route"]
        return {
            "question": state["question"],
            "generation": route.lower().strip(),
            "code": [],
            "data": [],
        }

    def _extract_route(self, state: State) -> str:
        """
        라우팅된 질문을 추출합니다.

        Args:
            state (dict): 현재 그래프 상태

        Returns:
            str: 라우팅된 질문
        """
        return state["generation"]

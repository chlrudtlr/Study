import streamlit as st
from custom_chatbot import DocumentChatbot

st.set_page_config(page_title="NVMe Spec 챗봇", layout="wide")
st.title("NVMe Spec 기반 챗봇")

documents_dir = "data/paper"
documents_description = "NVMe Base Specification 2.0e 문서"
force_reload = True


@st.cache_resource
def init_chatbot():
    chatbot = DocumentChatbot(documents_dir, documents_description, force_reload)
    return chatbot


if "chatbot" not in st.session_state:
    with st.spinner("NVMe Spec 챗봇 초기화 중입니다. 처음에는 시간이 조금 걸릴 수 있습니다."):
        st.session_state.chatbot = init_chatbot()
    st.success("초기화를 완료했습니다.")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
예시 질문:
- NVMe에서 Admin Command와 I/O Command의 차이는 무엇인가요?
- Identify Controller와 Identify Namespace의 차이를 설명해주세요.
- CAP 레지스터의 주요 필드는 무엇인가요?
- PRP와 SGL의 차이를 설명해주세요.
- NVMe spec에 없는 일반적인 SSD 상식도 알려줄 수 있나요?
"""
)

for conversation in st.session_state.messages:
    with st.chat_message(conversation["role"]):
        st.markdown(conversation["content"])

if prompt := st.chat_input("질문을 입력하세요."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중입니다..."):
            response = st.session_state.chatbot.invoke(prompt)

            answer_text = response["generation"]

            sources = response.get("sources", [])
            if sources:
                source_lines = ["", "**출처**"]
                for src in sources:
                    page = src.get("page", "N/A")
                    file_name = src.get("source", "Unknown")
                    source_lines.append(f"- {file_name}, page {page}")
                answer_text += "\n\n" + "\n".join(source_lines)

            st.markdown(answer_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer_text}
            )
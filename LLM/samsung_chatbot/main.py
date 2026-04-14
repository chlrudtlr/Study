import os

import numpy as np
import pandas as pd
import streamlit as st
from custom_chatbot import DocumentChatbot
from PIL import Image

# page title
st.set_page_config(page_title="🦜🕸️ 반도체 도메인 보고서 기반 챗봇")
st.title("🦜🕸️ 반도체 도메인 보고서 기반 챗봇")

documents_dir = "data/paper"

# 새로운 문서를 추가했다면, force_reload를 True로 변경하고, documents_description을 수정하세요.
documents_description = "차세대 반도체를 위한 글로벌 장비 개발 동향"

force_reload = False


@st.cache_resource
def init_chatbot():
    chatbot = DocumentChatbot(documents_dir, documents_description, force_reload)
    return chatbot


# Streamlit app은 app code를 계속 처음부터 재실행하는 방식으로 페이지를 갱신합니다.
# Chatbot을 state에 포함시키지 않으면 매 질문마다 chatbot을 다시 초기화 합니다.
if "chatbot" not in st.session_state:
    with st.spinner("챗봇 초기화 중입니다, 최대 3분까지 소요됩니다."):
        chatbot = init_chatbot()
        st.session_state.chatbot = chatbot
    st.write("챗봇 초기화를 완료했습니다.")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
- 예시 질문 (문서 활용): 차세대 반도체 생산 기술의 글로벌 동향을 설명해주세요.
- 예시 질문 (웹 검색 활용): 삼성전자 반도체의 장점을 설명해주세요.
"""
)

for conversation in st.session_state.messages:
    with st.chat_message(conversation["role"]):
        if "image" in conversation.keys() and conversation["image"]:
            st.image(conversation["content"])
        else:
            st.write(conversation["content"])

# React to user input
if prompt := st.chat_input("질문을 입력하면 챗봇이 답변을 제공합니다."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

if prompt is not None:
    response = st.session_state.chatbot.invoke(prompt)
    generation = response["generation"]
    with st.chat_message("assistant"):
        if "data" in response.keys() and "plot.png" in response["data"]:
            # Load image file on variable
            image = np.array(Image.open("plot.png"))
            # Display image
            st.image(image)
            st.session_state.messages.append(
                {"role": "assistant", "content": image, "image": True}
            )
            # Remove Image
            os.remove("plot.png")
        else:
            st.markdown(generation)
            st.session_state.messages.append(
                {"role": "assistant", "content": generation, "image": False}
            )

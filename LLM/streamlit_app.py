import streamlit as st


st.title("Streamlit 웹 애플리케이션 with Elice")

st.header('1. 정적 페이지 만들기')

st.markdown("""
            정적 페이지를 만드는 데에도 많은 요소가 활용될 수 있습니다.
            """)

st.code("""
        예를 들어 코드블럭은 코드를 쓰기도 좋지만, 글자를 강조하고 싶을때 사용해도 유효합니다.
        """)


st.caption("caption 기능은 인용구나, 각주등을 넣을 때 사용하기 좋습니다.")


name = st.text_input("text_input의 기능을 사용하여, 사람의 이름, 연락처 등 각종 사용자 입력을 받아볼 수 있습니다.",placeholder="홍길동")


if st.button('입력'):
    st.write(f'{name}님, 환영합니다.')

# input widget 실습
uploaded_file = st.file_uploader("Choose a csv file")
if uploaded_file:
    st.write("파일 이름: ",uploaded_file.name)
    
# 선택박스 widget
option = st.selectbox(
'How would you like to be contacted?',
('Email', 'Home phone', 'Mobile phone'))

st.write('You selected:', option)



with st.sidebar:
    add_selectbox = st.selectbox(
        "How would you like to be contacted? ",
        ("Email", "Home phone", "Mobile phone")
    )   
    add_radio = st.radio(
        "Choose a shipping method",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )

st.write(add_radio)
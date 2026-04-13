import streamlit as st

st.set_page_config(
    page_title="Streamlit 연습",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Streamlit 웹 애플리케이션 연습")
st.markdown("간단한 입력, 파일 업로드, 선택 위젯을 포함한 데모 페이지입니다.")

st.divider()

st.header("1. 사용자 정보 입력")

with st.form("welcome_form"):
    name = st.text_input(
        "이름을 입력하세요",
        placeholder="홍길동"
    )
    submitted = st.form_submit_button("입력")

if submitted:
    if name.strip():
        st.success(f"{name}님, 환영합니다!")
    else:
        st.warning("이름을 입력해주세요.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("2. 파일 업로드")
    uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])
    if uploaded_file:
        st.info(f"업로드된 파일: {uploaded_file.name}")

with col2:
    st.header("3. 연락 방식 선택")
    option = st.selectbox(
        "연락받고 싶은 방법을 선택하세요",
        ("Email", "Home phone", "Mobile phone")
    )
    st.write("선택한 방식:", option)

with st.sidebar:
    st.title("설정")
    add_selectbox = st.selectbox(
        "연락 방법",
        ("Email", "Home phone", "Mobile phone")
    )
    add_radio = st.radio(
        "배송 방법 선택",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )

st.divider()
st.subheader("사이드바 선택 결과")
st.write("배송 방법:", add_radio)

with st.expander("안내"):
    st.caption("이 앱은 Streamlit 기본 위젯 예제를 보기 좋게 정리한 예시입니다.")
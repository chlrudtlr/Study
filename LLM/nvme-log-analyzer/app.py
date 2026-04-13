import streamlit as st

# 페이지 설정
st.set_page_config(layout="wide")

# ------------------------
# CSS 설정
# ------------------------
st.markdown("""
<style>
/* 기본 Streamlit 여백 제거 */
section.main > div {
    padding-top: 0rem;
}
            
/* 전체 상단 여백 제거 */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
}
            
/* 제목 영역 */
.top-title {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 10px;
}

.title-text {
    font-size: 42px;
    font-weight: 700;
}

.made-by {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 6px;
}

/* 구분선 */
.top-line {
    border-top: 2px solid black;
    margin-top: 25px;
    margin-bottom: 25px;
}

</style>
""", unsafe_allow_html=True)

# ------------------------
# Header
# ------------------------
st.markdown("""
<div class="top-title">
    <div class="title-text">SVP2 TC Log 분석</div>
    <div class="made-by">Made by 최경식</div>
</div>
<div class="top-line"></div>
""", unsafe_allow_html=True)

# ------------------------
# 설명 영역
# ------------------------
st.markdown("""
#### 🟦 Log 분석 Tool 설명
간단한 웹 설명
""")

with st.expander("분석 Flow chart"):
    st.markdown("""
    - 어쩌구 저쩌구
    - 여기에다가 Flow chart 이미지 파일로 넣어야 겠다.
    """)

st.markdown("""
<div class="top-line"></div>
""", unsafe_allow_html=True)

# ------------------------
# 중간 영역 (업로드 + 요약)
# ------------------------
col1, col2 = st.columns(2)

# 파일 업로드
with col1:
    st.markdown("""
    #### 🟧 로그 파일 업로드(.txt)
    """)
    uploaded_files = st.file_uploader(
        "TXT 파일 업로드 (여러 개 가능)",
        type=["txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

# 요약 영역
with col2:
    st.markdown("""
    #### 🟨 분석 내용 요약
    """)
    with st.container(border=True):
        st.markdown("##### Test summary")
        st.write("이 영역은 텍스트 박스입니다.")
    # 예시
    st.metric("Error Count", 0)
    st.metric("Timeout", 0)
    st.metric("UECC", 0)

st.markdown("""
<div class="top-line"></div>
""", unsafe_allow_html=True)

# ------------------------
# 상세 분석 영역
# ------------------------
st.subheader("📄 상세 분석 결과")

st.write("여기에 상세 로그 분석 결과가 출력됩니다.")

# 예시 테이블
import pandas as pd

df = pd.DataFrame({
    "Time": [],
    "Type": [],
    "Message": []
})

st.dataframe(df, use_container_width=True)
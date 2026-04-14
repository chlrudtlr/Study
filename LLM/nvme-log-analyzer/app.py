import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------
# session_state 초기화
# ------------------------
if "selected_file_name" not in st.session_state:
    st.session_state.selected_file_name = None

if "selected_file_content" not in st.session_state:
    st.session_state.selected_file_content = None

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# ------------------------
# CSS 설정
# ------------------------
st.markdown("""
<style>
section.main > div {
    padding-top: 0rem;
}

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
}

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

.top-line {
    border-top: 2px solid black;
    margin-top: 25px;
    margin-bottom: 25px;
}

[data-testid="stTextArea"] textarea {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #f8f9fa !important;
    font-family: "Courier New", Consolas, monospace !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    cursor: text !important;
    opacity: 1 !important;
}

[data-testid="stTextArea"] textarea:disabled {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #f8f9fa !important;
    font-family: "Courier New", Consolas, monospace !important;
    cursor: text !important;
    opacity: 1 !important;
}

[data-testid="stTextArea"] {
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------
# 왼쪽 사이드바
# ------------------------
with st.sidebar:
    st.markdown("### 📘 NVMe Spec")

    st.link_button(
        "NVMe Spec 열기",
        "app/static/nvme_spec.pdf",
        use_container_width=True
    )

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
    st.markdown("#### 🟧 로그 파일 업로드(.txt)")

    uploaded_files = st.file_uploader(
        "TXT 파일 업로드 (여러 개 가능)",
        type=["txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        file_dict = {}

        for file in uploaded_files:
            raw_data = file.read()
            try:
                content = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                content = raw_data.decode("cp949", errors="replace")

            file_dict[file.name] = content

        # 1번, 2번 칸
        select_col, button_col = st.columns([2, 1])

        with select_col:
            selected_name = st.selectbox(
                "분석할 파일 선택",
                options=list(file_dict.keys()),
                index=0
            )

        with button_col:
            st.write("")
            st.write("")
            analyze_clicked = st.button("분석 시작", use_container_width=True)

        # 분석 시작 버튼 눌렀을 때만 분석 대상 저장
        if analyze_clicked:
            st.session_state.selected_file_name = selected_name
            st.session_state.selected_file_content = file_dict[selected_name]
            st.session_state.analysis_done = True

        # 선택된 파일만 표시
        if st.session_state.analysis_done and st.session_state.selected_file_name:
            st.markdown("##### 선택된 분석 대상 파일")

            with st.expander(f"📄 {st.session_state.selected_file_name}", expanded=True):
                st.text_area(
                    label="log",
                    value=st.session_state.selected_file_content,
                    height=350,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"log_{st.session_state.selected_file_name}"
                )

# 요약 영역
with col2:
    st.markdown("#### 🟨 분석 내용 요약")

    if st.session_state.analysis_done and st.session_state.selected_file_content:
        content = st.session_state.selected_file_content

        # 예시 분석 로직
        error_count = content.lower().count("error")
        timeout_count = content.lower().count("timeout")
        uecc_count = content.lower().count("uecc")

        with st.container(border=True):
            st.markdown("##### Test summary")
            st.write(f"선택된 파일: **{st.session_state.selected_file_name}**")
            st.write("분석 시작 버튼을 눌러 선택 파일에 대한 분석을 수행했습니다.")

        st.metric("Error Count", error_count)
        st.metric("Timeout", timeout_count)
        st.metric("UECC", uecc_count)

    else:
        with st.container(border=True):
            st.markdown("##### Test summary")
            st.write("파일을 선택한 뒤 '분석 시작' 버튼을 눌러주세요.")

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

if st.session_state.analysis_done and st.session_state.selected_file_content:
    content = st.session_state.selected_file_content
    lines = content.splitlines()

    results = []
    for idx, line in enumerate(lines, start=1):
        lower_line = line.lower()

        if "error" in lower_line:
            results.append({"Line": idx, "Type": "Error", "Message": line})
        elif "timeout" in lower_line:
            results.append({"Line": idx, "Type": "Timeout", "Message": line})
        elif "uecc" in lower_line:
            results.append({"Line": idx, "Type": "UECC", "Message": line})

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("선택한 파일에서 Error / Timeout / UECC 관련 로그를 찾지 못했습니다.")
else:
    st.write("여기에 상세 로그 분석 결과가 출력됩니다.")
    df = pd.DataFrame({
        "Line": [],
        "Type": [],
        "Message": []
    })
    st.dataframe(df, use_container_width=True)
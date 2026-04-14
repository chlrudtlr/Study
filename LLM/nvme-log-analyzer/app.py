import streamlit as st
import pandas as pd
import subprocess
import tempfile
from pathlib import Path

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

if "summary_output" not in st.session_state:
    st.session_state.summary_output = ""

if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = ""

# ------------------------
# C++ 자동 컴파일 + 실행 함수
# ------------------------
def run_cpp_parser(file_content: str) -> str:
    project_dir = Path(__file__).resolve().parent
    cpp_path = project_dir / "parser.cpp"
    exe_path = project_dir / "parser"

    if not cpp_path.exists():
        raise FileNotFoundError(f"parser.cpp 파일을 찾을 수 없습니다: {cpp_path}")

    # 1) parser.cpp 자동 컴파일
    compile_result = subprocess.run(
        ["g++", "-std=c++17", "-O2", str(cpp_path), "-o", str(exe_path)],
        capture_output=True,
        text=True
    )

    if compile_result.returncode != 0:
        raise RuntimeError(
            "C++ 컴파일 실패\n\n"
            f"{compile_result.stderr}"
        )

    # 2) 업로드된 txt 내용을 임시 파일로 저장
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8"
    ) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name

    # 3) 컴파일된 실행파일 자동 실행
    run_result = subprocess.run(
        [str(exe_path), temp_path],
        capture_output=True,
        text=True
    )

    # 임시 파일 삭제
    Path(temp_path).unlink(missing_ok=True)

    if run_result.returncode != 0:
        raise RuntimeError(
            "C++ 실행 실패\n\n"
            f"{run_result.stderr}"
        )

    return run_result.stdout.strip()

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
            
/* 분석 시작 버튼 위치 */
div.stButton {
    margin-top: 28px;
}

/* 분석 시작 버튼 스타일 */
div.stButton > button {
    background-color: white !important;
    color: #ff4d4f !important;
    border: 2px solid #ff4d4f !important;
    border-radius: 10px !important;
    height: 40px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

/* hover 효과 */
div.stButton > button:hover {
    background-color: #fff1f0 !important;
    color: #ff4d4f !important;
    border: 2px solid #ff4d4f !important;
}

/* 클릭 효과 */
div.stButton > button:active {
    background-color: #ffe3e3 !important;
    color: #ff4d4f !important;
    border: 2px solid #ff4d4f !important;
    transform: scale(0.98);
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

        select_col, button_col = st.columns([2, 1])

        with select_col:
            selected_name = st.selectbox(
                "분석할 파일 선택",
                options=list(file_dict.keys()),
                index=0
            )

        with button_col:
            analyze_clicked = st.button("분석 시작", use_container_width=True)

        if analyze_clicked:
            # 이전 분석 결과 초기화
            st.session_state.summary_output = ""
            st.session_state.analysis_error = ""
            st.session_state.analysis_done = False

            st.session_state.selected_file_name = selected_name
            st.session_state.selected_file_content = file_dict[selected_name]

            try:
                summary_result = run_cpp_parser(st.session_state.selected_file_content)

                # 결과 저장
                st.session_state.summary_output = summary_result
                st.session_state.analysis_done = True
                st.session_state.analysis_error = ""

            except Exception as e:
                st.session_state.summary_output = ""
                st.session_state.analysis_done = False
                st.session_state.analysis_error = str(e)

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

    if st.session_state.analysis_error:
        with st.container(border=True):
            st.markdown("##### Test summary")
            st.error(st.session_state.analysis_error)

    elif st.session_state.analysis_done:
        with st.container(border=True):
            st.markdown("##### Test summary")
            st.write(f"선택된 파일: **{st.session_state.selected_file_name}**")

            st.text_area(
                label="summary_output",
                value=st.session_state.summary_output,
                height=566,
                disabled=True,
                label_visibility="collapsed",
            )

    else:
        with st.container(border=True):
            st.markdown("##### Test summary")
            st.write("파일을 선택한 뒤 '분석 시작' 버튼을 눌러주세요.")

st.markdown("""
<div class="top-line"></div>
""", unsafe_allow_html=True)

# ------------------------
# 상세 분석 영역
# ------------------------
st.subheader("📄 상세 분석 결과")

if st.session_state.analysis_done and st.session_state.selected_file_content:
    lines = st.session_state.selected_file_content.splitlines()

    results = []
    for idx, line in enumerate(lines, start=1):
        if "Test Summary" in line:
            results.append({
                "Line": idx,
                "Type": "Test Summary",
                "Message": line
            })

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
    else:
        st.write('선택한 파일에서 "Test Summary"를 포함한 라인을 찾지 못했습니다.')
else:
    st.write("여기에 상세 로그 분석 결과가 출력됩니다.")
    df = pd.DataFrame({
        "Line": [],
        "Type": [],
        "Message": []
    })
    st.dataframe(df, use_container_width=True)
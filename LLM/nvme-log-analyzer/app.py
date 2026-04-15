import streamlit as st
import pandas as pd
import subprocess
import tempfile
import html
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

if "spec_chat_history" not in st.session_state:
    st.session_state.spec_chat_history = [
        {"role": "assistant", "content": "안녕하세요. NVMe Spec 관련 질문을 입력해주세요."}
    ]

if "spec_chat_input" not in st.session_state:
    st.session_state.spec_chat_input = ""

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

    return run_result.stdout

def parse_summary_output(summary_output: str):
    tc_name = "Unknown TC"
    details = ""
    summary = ""

    if "__TC_NAME__" not in summary_output or "__DETAILS__" not in summary_output:
        return tc_name, details, summary

    tc_split = summary_output.split("__TC_NAME__", 1)
    if len(tc_split) < 2:
        return tc_name, details, summary

    after_tc = tc_split[1]

    details_split = after_tc.split("__DETAILS__", 1)
    if len(details_split) < 2:
        return tc_name, details, summary

    tc_name = details_split[0].strip()

    after_details = details_split[1]

    if "__SUMMARY__" in after_details:
        details, summary = after_details.split("__SUMMARY__", 1)
        details = details.strip()
        summary = summary.strip()
    else:
        details = after_details.strip()

    return tc_name, details, summary

def format_details_text(details_text: str) -> str:
    lines = [line.strip() for line in details_text.splitlines() if line.strip()]
    result = []

    for line in lines:
        if line.startswith("- "):
            line = line[2:]

        if " : " in line:
            key, value = line.split(" : ", 1)
            formatted = f"<b>{html.escape(key)}</b> : {html.escape(value)}"
        elif ":" in line:
            key, value = line.split(":", 1)
            formatted = f"<b>{html.escape(key)}</b> : {html.escape(value)}"
        else:
            formatted = html.escape(line)

        result.append(formatted)

    return "<br>".join(result)

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
            
/* ------------------------ */
/* 사이드바 챗봇 UI */
/* ------------------------ */
.spec-chat-wrap {
    border: 1px solid #d9d9d9;
    border-radius: 12px;
    padding: 14px;
    margin-top: 18px;
    background: white;
}

.spec-chat-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 12px;
}

.spec-chat-desc {
    font-size: 13px;
    color: #666;
    margin-bottom: 10px;
}

.spec-chat-box {
    border: 1px solid #d9d9d9;
    border-radius: 10px;
    background: #fafafa;
    height: 360px;
    overflow-y: auto;
    padding: 10px;
    margin-bottom: 12px;
}

.spec-user-msg {
    background: #e6f4ff;
    padding: 10px 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 14px;
    white-space: pre-wrap;
}

.spec-bot-msg {
    background: #f6f6f6;
    padding: 10px 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 14px;
    white-space: pre-wrap;
}

.spec-chat-input-label {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
}
            
/* 분석 시작 버튼만 아래로 내리기 */
.analyze-btn-wrap {
    margin-top: 28px;
}

/* 챗봇 form submit 버튼은 위쪽 여백 제거 */
div[data-testid="stForm"] div.stButton {
    margin-top: 0 !important;
}

/* text_input 기본 여백 최소화 */
[data-testid="stTextInput"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
            
/* ------------------------ */
/* 분석 요약 3분할 영역 */
/* ------------------------ */
.summary-split-wrap {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
}

.summary-split-title {
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    height: 64px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    background: #ffffff;
    padding: 0 16px;
}

.summary-split-box {
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    background: #ffffff;
    box-sizing: border-box;
    padding: 16px;
    min-height: 180px;
    white-space: pre-wrap;

    font-size: 15px;
    line-height: 1.8;
    font-family: "Segoe UI", Arial, sans-serif;

    overflow-y: auto;
}

.summary-split-box.large {
    min-height: 220px;
}

.summary-empty-center {
    display: flex;
    align-items: center;
    justify-content: center;
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
        "app/static/NVM-Express-Base-Specification-2.0e-2024.07.29-Ratified.pdf",
        width="stretch"
    )

    st.markdown("### 💬 NVMe Spec Chatbot")
    st.markdown('<div class="spec-chat-desc">NVMe Spec 기반으로 질의응답을 할 수 있습니다.</div>', unsafe_allow_html=True)

    # 스크롤 가능한 대화 영역 시작
    chat_html = '<div class="spec-chat-box">'
    for msg in st.session_state.spec_chat_history:
        if msg["role"] == "user":
            chat_html += f'<div class="spec-user-msg">{msg["content"]}</div>'
        else:
            chat_html += f'<div class="spec-bot-msg">{msg["content"]}</div>'
    chat_html += '</div>'

    st.markdown(chat_html, unsafe_allow_html=True)

    st.markdown('<div class="spec-chat-input-label">질문 입력</div>', unsafe_allow_html=True)

    with st.form("spec_chat_form", clear_on_submit=True):
        input_col, btn_col = st.columns([4, 1], vertical_alignment="bottom")

        with input_col:
            user_question = st.text_input(
                label="NVMe Spec 질문 입력",
                key="spec_chat_input",
                placeholder="예: Identify Controller의 CSTS 필드 설명해줘",
                label_visibility="collapsed"
            )

        with btn_col:
            ask_clicked = st.form_submit_button("입력", width="stretch")

    if ask_clicked and user_question.strip():
        question = user_question.strip()

        st.session_state.spec_chat_history.append({
            "role": "user",
            "content": question
        })
        st.session_state.spec_chat_history.append({
            "role": "assistant",
            "content": f"(예시 응답) '{question}'에 대한 답변이 여기에 표시될 예정입니다."
        })

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

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

# 파일 업로드
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
        st.markdown('<div class="analyze-btn-wrap">', unsafe_allow_html=True)
        analyze_clicked = st.button("분석 시작", width="stretch", key="analyze_btn")
        st.markdown('</div>', unsafe_allow_html=True)

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
        st.markdown("##### 선택한 파일 전체 로그 보기")

        with st.expander(f"📄 {st.session_state.selected_file_name}", expanded=False):
            st.text_area(
                label="log",
                value=st.session_state.selected_file_content,
                height=350,
                disabled=True,
                label_visibility="collapsed",
                key=f"log_{st.session_state.selected_file_name}"
            )

st.markdown("""
<div class="top-line"></div>
""", unsafe_allow_html=True)

# 요약 영역
st.markdown("#### 🟨 분석 내용 요약")

if st.session_state.analysis_error:
    with st.container(border=True):
        st.markdown("##### Test summary")
        st.error(st.session_state.analysis_error)

elif st.session_state.analysis_done:
    tc_name, box1_text, box2_text = parse_summary_output(st.session_state.summary_output)

    title_text = f"Test Summary of [{tc_name}]"
    formatted_details = format_details_text(box1_text)

    if not box1_text:
        box1_text = ""
    if not box2_text:
        box2_text = "&nbsp;"

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="summary-split-wrap">
                <div class="summary-split-title">{title_text}</div>
                <div class="summary-split-box">{formatted_details}</div>
                <div class="summary-split-box large">{box2_text}</div>
            </div>
            """,
            unsafe_allow_html=True
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
        st.dataframe(df, width="stretch")
    else:
        st.write('선택한 파일에서 "Test Summary"를 포함한 라인을 찾지 못했습니다.')
else:
    st.write("여기에 상세 로그 분석 결과가 출력됩니다.")
    df = pd.DataFrame({
        "Line": [],
        "Type": [],
        "Message": []
    })
    st.dataframe(df, width="stretch")
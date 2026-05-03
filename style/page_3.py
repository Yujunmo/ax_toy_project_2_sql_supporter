import streamlit as st


def apply_page_3_css():
    st.markdown("""
<style>
:root {
    --shinhan-primary: #0054A4;
    --shinhan-hover: #003D7A;
    --shinhan-dark: #002D5A;
    --shinhan-light: #E8F1FB;
}

/* 버튼 스타일 - 흰색 배경에 신한 파란색 테두리 */
button {
    background-color: white !important;
    color: #0054A4 !important;
    border: 2px solid #0054A4 !important;
    font-weight: 600 !important;
}

button:hover {
    background-color: #E8F1FB !important;
    border-color: #0054A4 !important;
    box-shadow: 0 2px 8px rgba(0, 84, 164, 0.15) !important;
}

button:active {
    background-color: #D1E3F7 !important;
    border-color: #003D7A !important;
    color: #003D7A !important;
}

/* 메트릭 카드 스타일 */
[data-testid="metric-container"] {
    border-left: 4px solid #0054A4 !important;
    border-radius: 6px !important;
    padding: 12px !important;
}

/* Info, Success 박스 색상 */
.stAlert {
    border-radius: 6px !important;
}

/* 섹션 제목 색상 */
h2, h3 {
    color: #000000 !important;
}

/* 입력 필드 포커스 색상 */
input:focus, textarea:focus {
    border-color: #0054A4 !important;
}

/* 메인 제목 스타일 */
h1 {
    color: #000000 !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

import streamlit as st

def apply_css():
    # 페이지 레이아웃을 와이드로 설정
    st.set_page_config(layout="wide",
                        initial_sidebar_state="expanded"
                        ) 
    # st.markdown("""
    # <style>
    # /* 상단 공백 제거 */
    # .block-container {
    #     padding-top: 1rem !important;
    # }
    # [data-testid="stHeader"] {
    #     display: none !important;
    # }
    # .appview-container .main {
    #     padding-top: 5rem !important;
    # }
    # body {
    #     margin: 20px !important;
    #     padding: 20px !important;
    # }
    # .stTextArea textarea {
    #     width: 100% !important;
    # }
    # </style>
    # """, unsafe_allow_html=True)

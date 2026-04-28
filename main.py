import streamlit as st
import css

css.apply_css()
st.set_page_config(
    page_title="sql 보조기",
    layout="wide",
)

# 페이지 정의
page1 = st.Page("pages/page_1.py", title="dbLink주입기_#1")
page2 = st.Page("pages/page_2.py", title="dbLink주입기_#2")
page3 = st.Page("pages/page_3.py", title="table 추출기")

# 네비게이션 실행
pg = st.navigation([page1,page2,page3])
pg.run()
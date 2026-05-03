import streamlit as st
from modules.db.manager import init_db

init_db()
st.set_page_config(
    page_title="sql 보조기",
    layout="wide",
)

# 페이지 정의
#page1 = st.Page("pages/page_1.py", title="dbLink주입기_#1") # 서비스 제외
page2 = st.Page("pages/page_2.py", title="dbLink주입기")
page3 = st.Page("pages/page_3.py", title="데이터 이관 도구")
page4 = st.Page("pages/page_4.py", title="데이터 이관 확인")

# 네비게이션 실행
pg = st.navigation([page2,page3,page4])
pg.run()
import streamlit as st
import css
from modules.page_1.link_injector import graph
from modules.page_1.funcs import verification, verification_2

st.title("table 추출기")

# 페이지를 좌우로 나누기 (왼쪽을 더 넓게: 입력, 가운데: 버튼, 오른쪽: 결과)
col1, col2 = st.columns([2, 2])

with col1:
    query = st.text_area("여기에 쿼리를 입력하세요:", height=800)

with col2:
    pass


if st.button("추출하기"):
    if query.strip() == "" or query is None:
        st.write("쿼리를 입력해주세요.")
    else:
        try:
            with st.spinner("처리중.."): 
                result = graph.invoke({"query": query})
            st.write(result)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

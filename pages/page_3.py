import streamlit as st
from modules.page_3.table_extractor import graph
import pandas as pd

st.title("TABLE 추출기")
col1, col2 = st.columns([2, 2])

with col1:
    query = st.text_area("여기에 쿼리를 입력하세요:", height=700)

with col2:
    st.subheader("추출 결과", divider="blue")

    if 'result_df' in st.session_state:    
        col_title, col_count = st.columns([3, 1])
        with col_title:
            st.markdown("**Table List**")
        with col_count:
            st.caption(f"({len(st.session_state.result_df)}개)")
        st.dataframe(st.session_state.result_df, use_container_width=True)
    else:
        st.write("쿼리를 입력하고 '추출하기' 버튼을 눌러주세요.")


if st.button("추출하기"):
    if query.strip() == "" or query is None:
        st.write("쿼리를 입력해주세요.")
    else:
        try:
            with st.spinner("처리중.."): 
                result = graph.invoke({"query": query})
                print(f'graph result: {result['branch_A_answer']}' )
                st.session_state.result_df = pd.DataFrame(result['branch_A_answer'],columns=['Table List'])
                st.success("추출 완료")
            st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

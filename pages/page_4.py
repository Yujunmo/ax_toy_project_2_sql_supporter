import streamlit as st
from modules.db_manager import query_table, get_table_list
import pandas as pd

st.title("📊 Table 조회")

col1, col2 = st.columns([2, 1])

with col1:
    table_name = st.selectbox(
        "조회할 테이블 선택:",
        options=get_table_list(),
        index=0
    )

with col2:
    limit = st.number_input("조회 건수:", min_value=1, max_value=100, value=5)

if st.button("조회하기", type="primary"):
    data, error = query_table(table_name, limit=int(limit))

    if error:
        st.error(error)
    elif data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.caption(f"✓ {len(data)}건 조회됨")
    else:
        st.info("조회된 데이터가 없습니다.")

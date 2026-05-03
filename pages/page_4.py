import streamlit as st
from modules.db_manager import query_table, get_source_tables, get_target_table
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 기존 테이블 vs 이관 테이블 대조")
st.caption("원본 테이블과 이관 대상 테이블의 데이터를 양쪽에서 동시에 비교합니다")

# 설정 섹션
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    source_table = st.selectbox(
        "조회할 테이블 선택 (원본):",
        options=get_source_tables(),
        format_func=lambda x: f"{x} (원본)" if not x.endswith("_t") else x
    )

with col2:
    limit = st.number_input("조회 건수:", min_value=1, max_value=1000, value=50)

with col3:
    show_stats = st.checkbox("통계 표시", value=True)

if st.button("조회하기", type="primary", use_container_width=True):
    target_table = get_target_table(source_table)

    # 양쪽 데이터 조회
    source_data, source_error = query_table(source_table, limit=int(limit))
    target_data, target_error = query_table(target_table, limit=int(limit))

    # 에러 처리
    if source_error:
        st.error(f"❌ 원본 테이블 조회 실패: {source_error}")
    elif target_error:
        st.warning(f"⚠️ 이관 테이블 조회 실패: {target_error}")
    else:
        # 데이터 없음 처리
        if not source_data and not target_data:
            st.info("조회된 데이터가 없습니다.")
        else:
            # 통계 표시
            if show_stats:
                st.divider()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("원본 테이블", f"{len(source_data) if source_data else 0}건")
                with stat_col2:
                    st.metric("이관 테이블", f"{len(target_data) if target_data else 0}건")
                with stat_col3:
                    diff = (len(source_data) if source_data else 0) - (len(target_data) if target_data else 0)
                    status = "✓ 일치" if diff == 0 else f"⚠️ 차이: {abs(diff)}건"
                    st.metric("데이터 상태", status)
                st.divider()

            # 양쪽 데이터 표시
            col_source, col_target = st.columns(2)

            with col_source:
                st.subheader(f"📄 {source_table}")
                if source_data:
                    df_source = pd.DataFrame(source_data)
                    st.dataframe(df_source, use_container_width=True, height=400)
                    st.caption(f"✓ {len(source_data)}건 조회됨")
                else:
                    st.info("데이터 없음")

            with col_target:
                st.subheader(f"🎯 {target_table}")
                if target_data:
                    df_target = pd.DataFrame(target_data)
                    st.dataframe(df_target, use_container_width=True, height=400)
                    st.caption(f"✓ {len(target_data)}건 조회됨")
                else:
                    st.info("데이터 없음")

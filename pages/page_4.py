import streamlit as st
from modules.db.manager import query_table_filtered, get_source_tables, get_target_table
from style.page_4 import apply_page_4_css
import pandas as pd
apply_page_4_css()
st.set_page_config(layout="wide")

st.title("기존 테이블 vs 이관 테이블 대조")
st.caption("원본 테이블과 이관 대상 테이블의 데이터를 양쪽에서 동시에 비교합니다")
st.markdown("---")

# 설정 섹션
col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])

with col1:
    source_table = st.selectbox(
        "조회할 테이블 선택 :",
        options=get_source_tables()
    )

with col2:
    mncm_code = st.text_input("운용사코드 *", placeholder="예: E3069")

with col3:
    fund_code = st.text_input("펀드코드", placeholder="예: F001")

with col4:
    itms_code = st.text_input("Ticker", placeholder="예: 005930")

with col5:
    start_date = st.text_input("시작일자 *", placeholder="YYYYMMDD")

with col6:
    end_date = st.text_input("종료일자 *", placeholder="YYYYMMDD")

show_stats = st.checkbox("통계 표시", value=True)

if st.button("조회하기", type="primary", use_container_width=True):
    if not mncm_code:
        st.error("운용사코드를 입력해주세요.")
    elif not start_date:
        st.error("시작일자를 입력해주세요.")
    elif not end_date:
        st.error("종료일자를 입력해주세요.")
    else:
        target_table = get_target_table(source_table)

        source_data, source_error = query_table_filtered(
            source_table,
            mncm_code=mncm_code or None,
            fund_code=fund_code or None,
            itms_code=itms_code or None,
            start_date=start_date or None,
            end_date=end_date or None,
        )

        target_data, target_error = query_table_filtered(
            target_table,
            mncm_code=mncm_code or None,
            fund_code=fund_code or None,
            itms_code=itms_code or None,
            start_date=start_date or None,
            end_date=end_date or None,
        )

        if source_error:
            st.error(f"❌ 원본 테이블 조회 실패: {source_error}")
        elif target_error:
            st.warning(f"⚠️ 이관 테이블 조회 실패: {target_error}")
        else:
            if not source_data and not target_data:
                st.info("조회된 데이터가 없습니다.")
            else:
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

                col_source, col_target = st.columns(2)

                with col_source:
                    st.subheader(f"{source_table} [prod]")
                    if source_data:
                        df_source = pd.DataFrame(source_data)
                        st.dataframe(df_source, use_container_width=True, height=400)
                        st.caption(f"✓ {len(source_data)}건 조회됨")
                    else:
                        st.info("데이터 없음")

                with col_target:
                    st.subheader(f"{target_table} [test]")
                    if target_data:
                        df_target = pd.DataFrame(target_data)
                        st.dataframe(df_target, use_container_width=True, height=400)
                        st.caption(f"✓ {len(target_data)}건 조회됨")
                    else:
                        st.info("데이터 없음")

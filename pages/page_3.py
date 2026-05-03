import streamlit as st
from modules.page_3.table_extractor import graph
from modules.page_3.sql_generator import generate_sql_statements, format_sql_for_display
from modules.page_3.sql_executor import execute_multiple_statements
import pandas as pd

st.title("TABLE 추출기 & 마이그레이션")

# ===== 상단 입력 섹션 =====
st.subheader("이관 정보", divider="blue")

col1, col2, col3, col4, col5 = st.columns(5, gap="small")

with col1:
    mncm_code = st.text_input(
        "운용사코드",
        value="E3069",
        placeholder="예: E3069"
    )
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        extract_button = st.button("추출하기", type="primary", use_container_width=True)
    with btn_col2:
        generate_button = st.button("작성하기", use_container_width=True)               

with col2:
    fund_code = st.text_input(
        "펀드코드",
        value="FND001",
        placeholder="예: FND001"
    )
    btn_col3, btn_col4 = st.columns(2)     
    with btn_col3:
        execute_all_button = st.button("이관하기", use_container_width=True)
    with btn_col4:
        reset_button = st.button("초기화", use_container_width=True)

# ===== 초기화 버튼 기능 =====
if reset_button:
    # 모든 데이터 초기화
    if 'result_df' in st.session_state:
        del st.session_state.result_df
    if 'extracted_tables' in st.session_state:
        del st.session_state.extracted_tables
    if 'sql_statements' in st.session_state:
        del st.session_state.sql_statements
    if 'sql_edits' in st.session_state:
        del st.session_state.sql_edits
    if 'sql_selections' in st.session_state:
        del st.session_state.sql_selections

    st.toast("✓ 초기화 완료!", icon="🔄")
    st.rerun()

with col3:
    itms_code = st.text_input(
        "종목코드",
        value="",
        placeholder="예: 005930"
    )

with col4:
    start_date = st.text_input(
        "시작일자",
        value="20260301",
        placeholder="YYYYMMDD"
    )

with col5:
    end_date = st.text_input(
        "종료일자",
        value="20260430",
        placeholder="YYYYMMDD"
    )



# 입력값 검증 및 저장
if mncm_code and fund_code and start_date and end_date:
    migration_params = {
        'mncm_code': mncm_code,
        'fund_code': fund_code,
        'itms_code': itms_code,
        'start_date': start_date,
        'end_date': end_date
    }
    st.session_state.migration_params = migration_params

# ===== 테이블 추출 섹션 =====
st.subheader("테이블 추출", divider="blue")

col1, col2 = st.columns([2, 2])

with col1:
    query = st.text_area("여기에 쿼리를 입력하세요:", height=400)

with col2:
    st.subheader("추출 결과", divider="blue")

    if 'result_df' in st.session_state:
        col_title, col_count = st.columns([3, 1])
        with col_title:
            st.markdown("**Table List**")
        with col_count:
            st.caption(f"({len(st.session_state.result_df)}개)")
        st.dataframe(st.session_state.result_df, use_container_width=True)

        # 추출된 테이블 저장
        if 'extracted_tables' not in st.session_state:
            st.session_state.extracted_tables = st.session_state.result_df['Table List'].tolist()
    else:
        st.write("쿼리를 입력하고 '추출하기' 버튼을 눌러주세요.")


if extract_button:
    if query.strip() == "" or query is None:
        st.error("쿼리를 입력해주세요.")
    else:
        try:
            with st.spinner("처리중.."):
                result = graph.invoke({"query": query})
                st.session_state.result_df = pd.DataFrame(result['branch_A_answer'], columns=['Table List'])
                st.session_state.extracted_tables = result['branch_A_answer']

                # 이전 SQL 데이터 초기화
                if 'sql_statements' in st.session_state:
                    del st.session_state.sql_statements
                if 'sql_edits' in st.session_state:
                    del st.session_state.sql_edits
                if 'sql_selections' in st.session_state:
                    del st.session_state.sql_selections

            st.toast("✓ 추출 완료!", icon="✅")
            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")


# ===== SQL 작성 섹션 =====
if generate_button:
    if 'extracted_tables' not in st.session_state or not st.session_state.extracted_tables:
        st.error("먼저 테이블을 추출해주세요.")
    elif not( mncm_code and start_date and end_date) :
        if not mncm_code :
            st.error("이관 정보를 입력해주세요. (운용사코드)")
        if not start_date :
            st.error("이관 정보를 입력해주세요. (시작일자)")
        if not end_date :
            st.error("이관 정보를 입력해주세요. (종료일자)")   
        else:
            print("where?")
        
    else:
        try:
            with st.spinner("SQL 작성 중.."):
                sql_statements = generate_sql_statements(
                    extracted_tables=st.session_state.extracted_tables,
                    mncm_code=mncm_code,
                    fund_code=fund_code,
                    itms_code=itms_code,
                    start_date=start_date,
                    end_date=end_date
                )
                st.session_state.sql_statements = sql_statements

                # SQL 편집 상태 초기화 (새로운 기본값으로 설정)
                st.session_state.sql_edits = {}
                for idx, stmt in enumerate(sql_statements):
                    st.session_state.sql_edits[idx] = f"{stmt['delete_sql']}\n{stmt['insert_sql']}"

                # 하단 그리드 초기화 (체크박스 상태)
                st.session_state.sql_selections = [True] * len(sql_statements)

            st.toast("✓ SQL 작성 완료!", icon="✅")
            st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")


# ===== 생성된 SQL 표시 =====
if 'sql_statements' in st.session_state and st.session_state.sql_statements:
    st.subheader("생성된 SQL", divider="blue")

    # SQL 데이터 준비
    sql_data = []
    for stmt in st.session_state.sql_statements:
        sql_data.append({
            '테이블명': stmt['table_name'],
            'SQL 문': f"""{stmt['delete_sql']}\n{stmt['insert_sql']}""",
            '선택': False
        })

    # 데이터프레임 생성
    df_sql = pd.DataFrame(sql_data)

    # 체크박스와 함께 테이블 표시
    st.write("아래에서 실행할 SQL을 선택하세요:")

    # 헤더
    col1, col2, col3, col4 = st.columns([0.8, 1, 3.2, 0.8])
    with col1:
        st.markdown("**선택**")
    with col2:
        st.markdown("**테이블명**")
    with col3:
        st.markdown("**SQL 문 (DELETE / INSERT)**")
    with col4:
        st.markdown("**실행**")

    # 선택 상태 저장 (길이 동적 조정)
    if 'sql_selections' not in st.session_state or len(st.session_state.sql_selections) != len(st.session_state.sql_statements):
        st.session_state.sql_selections = [True] * len(st.session_state.sql_statements)

    # 각 행 표시
    for idx, stmt in enumerate(st.session_state.sql_statements):
        col1, col2, col3, col4 = st.columns([0.8, 1, 3.2, 0.8])

        with col1:
            st.session_state.sql_selections[idx] = st.checkbox(
                "선택",
                value=st.session_state.sql_selections[idx],
                key=f"sql_checkbox_{idx}",
                label_visibility="collapsed"
            )

        with col2:
            st.write(f"**{stmt['table_name']}**")

        with col3:
            # 편집 가능한 텍스트 박스
            default_sql = f"{stmt['delete_sql']}\n{stmt['insert_sql']}"

            edited_sql = st.text_area(
                "SQL 편집",
                value=st.session_state.sql_edits.get(idx, default_sql) if 'sql_edits' in st.session_state else default_sql,
                height=150,
                key=f"sql_textarea_{idx}",
                label_visibility="collapsed"
            )

            # 편집된 SQL 저장
            if 'sql_edits' not in st.session_state:
                st.session_state.sql_edits = {}
            st.session_state.sql_edits[idx] = edited_sql

        with col4:
            if st.button(
                "실행",
                key=f"run_button_{idx}"
            ):
                # 해당 행의 편집된 SQL 가져오기
                if 'sql_edits' in st.session_state and idx in st.session_state.sql_edits:
                    sql_to_execute = st.session_state.sql_edits[idx]

                    # SQL 실행
                    success, message, affected_rows = execute_multiple_statements(sql_to_execute)

                    # 결과 표시
                    if success:
                        st.success(f"✓ {message}")
                    else:
                        st.error(f"✗ {message}")

    # 선택된 SQL 요약
    selected_count = sum(st.session_state.sql_selections)
    if selected_count > 0:
        st.info(f"{selected_count}개의 SQL이 선택되었습니다.")


# ===== 일괄 실행 섹션 =====
if execute_all_button:
    # 선택된 항목이 있는지 확인
    if 'sql_statements' not in st.session_state or not st.session_state.sql_statements:
        st.error("생성된 SQL이 없습니다.")
    elif not any(st.session_state.sql_selections):
        st.error("선택된 SQL이 없습니다.")
    else:
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'affected_rows': 0,
            'success_list': [],
            'errors': []
        }

        with st.spinner("SQL 일괄 실행 중.."):
            for idx, stmt in enumerate(st.session_state.sql_statements):
                # 선택된 항목만 처리
                if not st.session_state.sql_selections[idx]:
                    continue

                results['total'] += 1

                # 편집된 SQL 가져오기
                sql_to_execute = st.session_state.sql_edits.get(idx, "")

                try:
                    # SQL 실행
                    success, message, affected_rows = execute_multiple_statements(sql_to_execute)

                    if success:
                        results['success'] += 1
                        results['affected_rows'] += affected_rows
                        results['success_list'].append({
                            'table_name': stmt['table_name'],
                            'index': idx,
                            'message': message,
                            'affected_rows': affected_rows
                        })
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'table_name': stmt['table_name'],
                            'index': idx,
                            'error': message
                        })

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'table_name': stmt['table_name'],
                        'index': idx,
                        'error': str(e)
                    })

        # 결과 표시
        st.subheader("실행 결과", divider="green")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 실행", results['total'])
        with col2:
            st.metric("성공", results['success'])
        with col3:
            st.metric("실패", results['failed'])
        with col4:
            st.metric("영향받은 행", results['affected_rows'])

        # 성공한 항목 표시
        if results['success_list']:
            st.success(f"성공한 항목: {results['success']}개")
            with st.expander("성공 항목 상세보기"):
                for item in results['success_list']:
                    st.markdown(f"**{item['table_name']}** (Row {item['index']})")
                    st.caption(f"{item['message']}")

        # 에러 목록 표시
        if results['errors']:
            st.error(f"실패한 항목: {results['failed']}개")
            with st.expander("실패 항목 상세보기"):
                for error in results['errors']:
                    st.markdown(f"**{error['table_name']}** (Row {error['index']})")
                    st.code(error['error'])
        elif results['success'] > 0:
            st.success("모든 선택된 SQL이 성공적으로 실행되었습니다!")

        st.toast("✓ 일괄 실행 완료!", icon="✅")

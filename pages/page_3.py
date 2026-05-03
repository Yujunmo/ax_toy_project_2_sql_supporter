import streamlit as st
import streamlit.components.v1 as components
import time
from modules.agents.table_extractor import graph
from modules.sql.generator import generate_sql_statements, format_sql_for_display
from modules.sql.executor import execute_multiple_statements
from style.page_3 import apply_page_3_css
import pandas as pd
apply_page_3_css()

st.title("데이터 이관")

# ===== 상단 입력 섹션 =====
st.markdown("---")
st.subheader("이관 정보")

col1, col2, col3, col4, col5 = st.columns(5, gap="small")

with col1:
    mncm_code = st.text_input(
        "운용사코드",
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
    )
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        auto_run_button = st.button("자동실행", use_container_width=True)    
    with btn_col2:
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
    if 'suffix_filters' in st.session_state:
        del st.session_state.suffix_filters
    if 'input_query' in st.session_state:
        del st.session_state.input_query

    # 개별 체크박스 위젯 세션값 삭제
    for key in [k for k in st.session_state if k.startswith('sql_checkbox_') or k.startswith('suffix_filter_')]:
        del st.session_state[key]

    # query 위젯 강제 초기화 (key 변경)
    st.session_state.query_version = st.session_state.get('query_version', 0) + 1

    st.toast("✓ 초기화 완료!")
    st.rerun()

with col3:
    itms_code = st.text_input(
        "종목코드",
        value="",
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
st.markdown('<div id="table-extract"></div>', unsafe_allow_html=True)

if st.session_state.get('scroll_to_extract'):
    st.session_state.scroll_to_extract = False
    components.html("""
<script>
    window.parent.document.getElementById('table-extract').scrollIntoView({behavior: 'smooth'});
</script>
""", height=0)

st.markdown("---")

col1, col2 = st.columns([2, 1.5])

with col1:
    st.subheader("테이블 추출")
    query = st.text_area(
        "여기에 쿼리를 입력하세요:",
        height=400,
        key=f"query_{st.session_state.get('query_version', 0)}",
        value=st.session_state.get("input_query", "")
    )
    if query:
        st.session_state["input_query"] = query

with col2:
    st.subheader("추출 결과")

    if 'result_df' in st.session_state:
        col_title, col_count = st.columns([3, 1])
        with col_title:
            st.markdown("**Table List**")
        with col_count:
            elapsed = st.session_state.get('extract_elapsed', '')
            elapsed_str = f"{elapsed}s" if elapsed else ""
            st.caption(f"(개수:{len(st.session_state.result_df)}개/시간 : {elapsed_str})")
        st.dataframe(st.session_state.result_df, use_container_width=True)

        # 추출된 테이블 저장
        if 'extracted_tables' not in st.session_state:
            st.session_state.extracted_tables = st.session_state.result_df['Table List'].tolist()
    else:
        st.write("쿼리를 입력하고 '추출하기' 버튼을 눌러주세요.")


if extract_button:
    if query is None or query.strip() == "":
        st.error("쿼리를 입력해주세요.")
    else:
        try:
            with st.spinner("처리중.."):
                _t0 = time.time()
                result = graph.invoke({"query": query})
                st.session_state.extract_elapsed = round(time.time() - _t0, 2)
                st.session_state.result_df = pd.DataFrame(result['branch_A_answer'], columns=['Table List'])
                st.session_state.extracted_tables = result['branch_A_answer']

                # 이전 SQL 데이터 초기화
                if 'sql_statements' in st.session_state:
                    del st.session_state.sql_statements
                if 'sql_edits' in st.session_state:
                    del st.session_state.sql_edits
                if 'sql_selections' in st.session_state:
                    del st.session_state.sql_selections
                if 'suffix_filters' in st.session_state:
                    del st.session_state.suffix_filters

            st.session_state.scroll_to_extract = True
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

                # 위젯 key를 변경하여 새로운 텍스트에어를 강제로 재생성
                if 'sql_version' not in st.session_state:
                    st.session_state.sql_version = 0
                st.session_state.sql_version += 1
                st.session_state.scroll_to_sql = True

            st.toast("✓ SQL 작성 완료!", icon="✅")
            st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")


# ===== 생성된 SQL 표시 =====
if 'sql_statements' in st.session_state and st.session_state.sql_statements:
    st.markdown('<div id="generated-sql"></div>', unsafe_allow_html=True)

    if st.session_state.get('scroll_to_sql'):
        st.session_state.scroll_to_sql = False
        components.html("""
<script>
    window.parent.document.getElementById('generated-sql').scrollIntoView({behavior: 'smooth'});
</script>
""", height=0)

    st.markdown("---")
    st.subheader("생성된 SQL")
    col1, col2 = st.columns([2, 1.5])

    # 접미사 필터: sql_statements에서 고유 접미사 추출
    all_suffixes = sorted(set(stmt['table_name'].split('_')[-1] for stmt in st.session_state.sql_statements))
    if 'suffix_filters' not in st.session_state or set(st.session_state.suffix_filters.keys()) != set(all_suffixes):
        st.session_state.suffix_filters = {s: True for s in all_suffixes}

    with col1:
        st.markdown("**접미사 필터**")
        filter_cols = st.columns(len(all_suffixes) * 2)
        for i, suffix in enumerate(all_suffixes):
            with filter_cols[i]:
                
                st.session_state.suffix_filters[suffix] = st.checkbox(
                    f"_{suffix}"[1:],
                    value=st.session_state.suffix_filters[suffix],
                    key=f"suffix_filter_{suffix}"
                )

    execute_all_button = st.button("이관하기", use_container_width=True)

    # 진행 상황 표시 (이관하기 버튼 바로 아래)
    progress_bar = st.progress(0)
    status_text = st.empty()

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
        suffix = stmt['table_name'].split('_')[-1]
        if not st.session_state.suffix_filters.get(suffix, True):
            continue
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
                key=f"sql_textarea_{idx}_{st.session_state.get('sql_version', 0)}",
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

    # 선택된 SQL 요약 (필터 적용)
    selected_count = sum(
        selected
        for idx, (stmt, selected) in enumerate(zip(st.session_state.sql_statements, st.session_state.sql_selections))
        if st.session_state.suffix_filters.get(stmt['table_name'].split('_')[-1], True) and selected
    )
    if selected_count > 0:
        st.info(f"{selected_count}개의 SQL이 선택되었습니다.")


# ===== 일괄 실행 섹션 & 자동 실행의 실행 섹션 =====
if 'sql_statements' in st.session_state and st.session_state.sql_statements:
    should_execute = execute_all_button or st.session_state.get('auto_run_execute')
    if should_execute:
        if st.session_state.get('auto_run_execute'):
            st.session_state.auto_run_execute = False
        filtered_selected = any(
            st.session_state.sql_selections[idx]
            for idx, stmt in enumerate(st.session_state.sql_statements)
            if st.session_state.suffix_filters.get(stmt['table_name'].split('_')[-1], True)
        )
        if not filtered_selected:
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
                total_to_run = sum(
                    1 for i, s in enumerate(st.session_state.sql_statements)
                    if st.session_state.suffix_filters.get(s['table_name'].split('_')[-1], True)
                    and st.session_state.sql_selections[i]
                )
                done = 0

                for idx, stmt in enumerate(st.session_state.sql_statements):
                    # 접미사 필터 및 체크박스 선택 항목만 처리
                    suffix = stmt['table_name'].split('_')[-1]
                    if not st.session_state.suffix_filters.get(suffix, True):
                        continue
                    if not st.session_state.sql_selections[idx]:
                        continue

                    results['total'] += 1
                    status_text.caption(f"처리 중 ({done + 1}/{total_to_run}): {stmt['table_name']}")

                    # 편집된 SQL 가져오기
                    sql_to_execute = st.session_state.sql_edits.get(idx, "")

                    try:
                        # SQL 실행
                        if stmt['table_name'][-2:] != "bs":
                            time.sleep(0.5) # 시연용 코드 ( 추후 삭제할 것 )
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

                    done += 1
                    progress_bar.progress(done / total_to_run)

            status_text.success(f"✓ 모든 SQL 실행 완료! ({done}/{total_to_run})")

            # 결과 표시
            st.markdown('<div id="execution-result"></div>', unsafe_allow_html=True)
            components.html("""
<script>
    window.parent.document.getElementById('execution-result').scrollIntoView({behavior: 'smooth'});
</script>
""", height=0)
            st.markdown("---")
            st.subheader("실행 결과")

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


# ===== 자동실행 섹션 =====
if auto_run_button:
    # 입력값 검증
    missing = []
    if not query or query.strip() == "":
        missing.append("쿼리")
    if not mncm_code:
        missing.append("운용사코드")
    if not start_date:
        missing.append("시작일자")
    if not end_date:
        missing.append("종료일자")

    if missing:
        st.error(f"필수 입력값을 확인해주세요: {', '.join(missing)}")
    else:
        try:
            # ① 추출
            with st.spinner("① 테이블 추출 중.."):
                _t0 = time.time()
                result = graph.invoke({"query": query})
                st.session_state.extract_elapsed = round(time.time() - _t0, 2)
                extracted_tables = result['branch_A_answer']
                st.session_state.result_df = pd.DataFrame(extracted_tables, columns=['Table List'])
                st.session_state.extracted_tables = extracted_tables

            st.toast(f"① 추출 완료 ({st.session_state.extract_elapsed}s)", icon="✅")

            # ② SQL 작성
            
            with st.spinner("② SQL 작성 중.."):
                sql_statements = generate_sql_statements(
                    extracted_tables=extracted_tables,
                    mncm_code=mncm_code,
                    fund_code=fund_code,
                    itms_code=itms_code,
                    start_date=start_date,
                    end_date=end_date
                )
                st.session_state.sql_statements = sql_statements
                st.session_state.sql_edits = {
                    idx: f"{stmt['delete_sql']}\n{stmt['insert_sql']}"
                    for idx, stmt in enumerate(sql_statements)
                }
                st.session_state.sql_selections = [True] * len(sql_statements)
                if 'sql_version' not in st.session_state:
                    st.session_state.sql_version = 0
                st.session_state.sql_version += 1

            st.toast(f"② SQL 작성 완료 ({len(sql_statements)}개)", icon="✅")

            # 생성된 SQL 섹션으로 이동 후, 자동 실행 플래그 설정
            st.session_state.scroll_to_sql = True
            st.session_state.auto_run_execute = True
            st.rerun()

        except Exception as e:
            st.error(f"자동실행 중 오류가 발생했습니다: {e}")

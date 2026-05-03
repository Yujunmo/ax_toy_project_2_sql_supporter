# Page 3 - Database 통합 예제

page_3에서 테이블 추출 후 데이터베이스에 저장하는 방법을 설명합니다.

## 현재 워크플로우 (page_3.py)

```python
# 현재: 테이블 추출 후 화면에만 표시
result = graph.invoke({"query": query})
st.session_state.result_df = pd.DataFrame(result['branch_A_answer'], columns=['Table List'])
```

## DB 통합 후 워크플로우 (예정)

### Phase 1: 테이블 추출 + DB 저장 (현재 구현)

```python
from modules.db_manager import create_migration_job
from modules.page_3.table_extractor import graph
import json

# 1. 테이블 추출
result = graph.invoke({"query": query})
extracted_tables = result['branch_A_answer']

# 2. 마이그레이션 작업 생성 및 저장
job_id = create_migration_job(
    source_sql=query,
    extracted_tables=extracted_tables
)

# 3. 화면에 표시
st.session_state.result_df = pd.DataFrame(extracted_tables, columns=['Table List'])
st.session_state.job_id = job_id
st.success(f"✓ 추출 완료 (Job ID: {job_id})")
```

### Phase 2: DELETE/INSERT SQL 자동 생성 (추후)

```python
from modules.db_manager import add_migration_detail

# 추출된 각 테이블에 대해 DELETE/INSERT SQL 생성
for table_name in extracted_tables:
    # LLM을 사용하여 DELETE/INSERT SQL 자동 생성
    delete_sql = generate_delete_sql(table_name, query)
    insert_sql = generate_insert_sql(table_name, query)
    
    # 데이터베이스에 저장
    detail_id = add_migration_detail(
        job_id=job_id,
        table_name=table_name,
        delete_sql=delete_sql,
        insert_sql=insert_sql
    )
```

### Phase 3: SQL 실행 및 검증 (추후)

```python
from modules.db_manager import (
    update_migration_detail_status,
    add_validation_result,
    update_migration_job_status
)

# 각 DELETE/INSERT SQL 실행
for detail in get_migration_details(job_id):
    try:
        # DELETE 실행
        execute_sql(detail['delete_sql'])
        
        # INSERT 실행
        cursor = execute_sql(detail['insert_sql'])
        affected_rows = cursor.rowcount
        
        # 성공 기록
        update_migration_detail_status(
            detail_id=detail['detail_id'],
            status="success",
            affected_rows=affected_rows
        )
    except Exception as e:
        # 실패 기록
        update_migration_detail_status(
            detail_id=detail['detail_id'],
            status="failed",
            error_msg=str(e)
        )

# 전체 작업 완료 표시
update_migration_job_status(job_id=job_id, status="completed")
```

## 통합 시 수정할 파일

### page_3.py (수정 필요)

```python
import streamlit as st
from modules.page_3.table_extractor import graph
from modules.db_manager import create_migration_job, get_migration_job
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
        
        # ★ 새로 추가: Job ID 표시
        if 'job_id' in st.session_state:
            st.caption(f"Job ID: {st.session_state.job_id}")
    else:
        st.write("쿼리를 입력하고 '추출하기' 버튼을 눌러주세요.")


if st.button("추출하기"):
    if query.strip() == "" or query is None:
        st.write("쿼리를 입력해주세요.")
    else:
        try:
            with st.spinner("처리중.."): 
                # 테이블 추출
                result = graph.invoke({"query": query})
                extracted_tables = result['branch_A_answer']
                
                # ★ 새로 추가: DB에 마이그레이션 작업 생성
                job_id = create_migration_job(
                    source_sql=query,
                    extracted_tables=extracted_tables
                )
                
                # UI 업데이트
                st.session_state.result_df = pd.DataFrame(extracted_tables, columns=['Table List'])
                st.session_state.job_id = job_id  # ★ 새로 추가
                st.success(f"✓ 추출 완료 (Job ID: {job_id})")
            st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
```

## 테스트 방법

```bash
# 1. 프로젝트 루트에서 Streamlit 실행
streamlit run main.py

# 2. page_3 (table 추출기) 선택

# 3. SQL 입력 예시:
# SELECT u.id, u.name, o.order_id, o.order_date
# FROM users u
# JOIN orders o ON u.id = o.user_id
# JOIN products p ON o.product_id = p.id

# 4. "추출하기" 버튼 클릭

# 5. 데이터베이스 확인:
sqlite3 data_migration.db
> SELECT * FROM migration_jobs ORDER BY job_id DESC LIMIT 1;
> SELECT * FROM migration_details WHERE job_id = (최신 job_id);
```

## 다음 단계

1. ✅ **DB 설정**: 데이터베이스 초기화 완료
2. ⏳ **Page 3 통합**: page_3.py에 create_migration_job 호출 추가
3. ⏳ **SQL 자동 생성**: LLM을 사용하여 DELETE/INSERT SQL 자동 생성
4. ⏳ **SQL 실행 페이지**: 새 페이지(page_4)에서 SQL 실행 및 검증


# 빠른 시작 가이드

## 📋 데이터베이스 구조

```
migration_jobs (마이그레이션 작업)
├── job_id (PK)
├── created_at
├── source_sql          ← 사용자 입력 SQL
├── extracted_tables    ← 추출된 테이블 목록 (JSON)
├── status              ← pending/in_progress/completed/failed
└── notes

migration_details (각 테이블별 이관 내역)
├── detail_id (PK)
├── job_id (FK) → migration_jobs.job_id
├── table_name
├── delete_sql          ← DELETE SQL (자동 생성 예정)
├── insert_sql          ← INSERT SQL (자동 생성 예정)
├── executed_at
├── execution_status    ← pending/success/failed
├── affected_rows       ← 영향받은 행 수
└── error_message

migration_validation (검증 결과)
├── validation_id (PK)
├── job_id (FK) → migration_jobs.job_id
├── table_name
├── source_count        ← 원본 데이터 행 수
├── target_count        ← 대상 데이터 행 수
├── validation_passed   ← 검증 성공 여부
└── validated_at
```

## 🚀 기본 사용법

### 1️⃣ 마이그레이션 작업 생성
```python
from modules.db_manager import create_migration_job

job_id = create_migration_job(
    source_sql="SELECT * FROM users u JOIN orders o ON u.id = o.user_id",
    extracted_tables=["users", "orders"]
)
# job_id = 1 (첫 번째 작업)
```

### 2️⃣ 작업 정보 조회
```python
from modules.db_manager import get_migration_job

job = get_migration_job(job_id=1)
print(job['status'])            # 'pending'
print(job['extracted_tables'])  # '["users", "orders"]'
```

### 3️⃣ 테이블별 마이그레이션 SQL 추가
```python
from modules.db_manager import add_migration_detail

# users 테이블
detail_id_1 = add_migration_detail(
    job_id=1,
    table_name="users",
    delete_sql="DELETE FROM users WHERE id > 1000",
    insert_sql="INSERT INTO users SELECT * FROM source.users WHERE id > 1000"
)

# orders 테이블
detail_id_2 = add_migration_detail(
    job_id=1,
    table_name="orders",
    delete_sql="DELETE FROM orders WHERE created_at > '2023-01-01'",
    insert_sql="INSERT INTO orders SELECT * FROM source.orders WHERE created_at > '2023-01-01'"
)
```

### 4️⃣ SQL 실행 결과 기록
```python
from modules.db_manager import update_migration_detail_status

# 성공
update_migration_detail_status(
    detail_id=1,
    status="success",
    affected_rows=500
)

# 실패
update_migration_detail_status(
    detail_id=2,
    status="failed",
    error_msg="Foreign key constraint violation"
)
```

### 5️⃣ 검증 결과 저장
```python
from modules.db_manager import add_validation_result

add_validation_result(
    job_id=1,
    table_name="users",
    source_count=1500,
    target_count=1500,
    passed=True
)
```

### 6️⃣ 상태 조회
```python
from modules.db_manager import get_migration_details, get_validation_results

# 마이그레이션 상세 정보
details = get_migration_details(job_id=1)
for detail in details:
    print(f"{detail['table_name']}: {detail['execution_status']}")

# 검증 결과
validations = get_validation_results(job_id=1)
for v in validations:
    print(f"{v['table_name']}: {v['source_count']} → {v['target_count']}")
```

## 📊 Streamlit 통합 예제

### Page 3 (테이블 추출)에서 사용
```python
import streamlit as st
from modules.page_3.table_extractor import graph
from modules.db_manager import create_migration_job

if st.button("추출하기"):
    result = graph.invoke({"query": query})
    extracted_tables = result['branch_A_answer']
    
    # DB에 저장
    job_id = create_migration_job(
        source_sql=query,
        extracted_tables=extracted_tables
    )
    
    st.success(f"✓ 추출 완료 (Job ID: {job_id})")
```

### Page 4 (마이그레이션 실행)에서 사용 (추후)
```python
import streamlit as st
from modules.db_manager import (
    get_migration_details,
    update_migration_detail_status
)

job_id = st.number_input("Job ID", min_value=1)

if st.button("마이그레이션 실행"):
    details = get_migration_details(job_id)
    
    for detail in details:
        try:
            # SQL 실행 (예시)
            # execute_sql(detail['delete_sql'])
            # execute_sql(detail['insert_sql'])
            # affected_rows = cursor.rowcount
            
            update_migration_detail_status(
                detail_id=detail['detail_id'],
                status="success",
                affected_rows=100
            )
        except Exception as e:
            update_migration_detail_status(
                detail_id=detail['detail_id'],
                status="failed",
                error_msg=str(e)
            )
```

## 🔍 SQL로 직접 조회

### 가장 최근 작업 조회
```sql
SELECT * FROM migration_jobs ORDER BY job_id DESC LIMIT 1;
```

### 특정 작업의 모든 상세 정보
```sql
SELECT * FROM migration_details WHERE job_id = 1 ORDER BY table_name;
```

### 실패한 마이그레이션
```sql
SELECT * FROM migration_details WHERE execution_status = 'failed';
```

### 검증 결과 조회
```sql
SELECT * FROM migration_validation WHERE job_id = 1;
```

## 📁 파일 구조

```
프로젝트루트/
├── main.py                          (수정: init_db() 추가)
├── data_migration.db                (자동 생성)
├── DB_GUIDE.md                      (상세 설명서)
├── DB_SETUP_COMPLETE.md             (설정 완료 보고)
├── QUICK_START.md                   (이 파일)
├── requirements.txt
├── modules/
│   ├── db_manager.py                (새로 추가: DB 헬퍼 함수)
│   └── page_3/
│       ├── table_extractor.py       (기존)
│       ├── CLAUDE.md                (기존)
│       └── INTEGRATION_EXAMPLE.md   (새로 추가: 통합 예제)
└── pages/
    ├── page_1.py
    ├── page_2.py
    └── page_3.py
```

## ⚡ 팁

### JSON 파싱이 필요한 경우
```python
import json
from modules.db_manager import get_migration_job

job = get_migration_job(1)
tables = json.loads(job['extracted_tables'])  # ["users", "orders"]
```

### 모든 최근 작업 조회
```python
from modules.db_manager import list_migration_jobs

jobs = list_migration_jobs(limit=10)
for job in jobs:
    print(f"Job {job['job_id']}: {job['status']} - {job['created_at']}")
```

### 데이터베이스 초기화 (필요 시)
```python
from modules.db_manager import init_db
init_db()  # 새로운 빈 데이터베이스 생성
```

---

더 자세한 내용은 [DB_GUIDE.md](DB_GUIDE.md)를 참고하세요.

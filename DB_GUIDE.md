# 데이터 이관 데이터베이스 가이드

## 개요

SQLite 기반의 데이터 이관 추적 시스템입니다. 사용자가 입력한 SQL에서 추출된 테이블 정보와 이관 작업 이력을 관리합니다.

## 데이터베이스 위치

```
프로젝트루트/data_migration.db
```

## 데이터베이스 구조

### 1. migration_jobs (마이그레이션 작업)

사용자가 SQL을 입력하고 테이블을 추출한 각 작업의 기본 정보를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| job_id | INTEGER | 작업 ID (자동 증가) |
| created_at | TIMESTAMP | 작업 생성 시간 |
| source_sql | TEXT | 사용자가 입력한 원본 SQL |
| extracted_tables | TEXT (JSON) | 추출된 테이블 목록 (JSON 형식) |
| status | TEXT | 작업 상태 (pending/in_progress/completed/failed) |
| notes | TEXT | 작업 메모 |

**예시:**
```sql
SELECT * FROM migration_jobs WHERE job_id = 1;
```

### 2. migration_details (마이그레이션 상세 정보)

각 테이블별 DELETE/INSERT SQL 실행 이력을 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| detail_id | INTEGER | 상세 정보 ID |
| job_id | INTEGER (FK) | 마이그레이션 작업 ID |
| table_name | TEXT | 테이블 이름 |
| delete_sql | TEXT | DELETE SQL (선택사항) |
| insert_sql | TEXT | INSERT SQL (선택사항) |
| executed_at | TIMESTAMP | 실행 시간 |
| execution_status | TEXT | 실행 상태 (pending/success/failed) |
| affected_rows | INTEGER | 영향받은 행 수 |
| error_message | TEXT | 오류 메시지 |

### 3. migration_validation (검증 결과)

이관 전후 데이터 검증 결과를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| validation_id | INTEGER | 검증 ID |
| job_id | INTEGER (FK) | 마이그레이션 작업 ID |
| table_name | TEXT | 테이블 이름 |
| source_count | INTEGER | 원본 행 수 |
| target_count | INTEGER | 대상 행 수 |
| validation_passed | BOOLEAN | 검증 성공 여부 |
| validated_at | TIMESTAMP | 검증 시간 |

## 사용 예시

### 1. 새 마이그레이션 작업 생성

```python
from modules.db_manager import create_migration_job

job_id = create_migration_job(
    source_sql="SELECT * FROM users u JOIN orders o ON u.id = o.user_id",
    extracted_tables=["users", "orders"]
)
print(f"Created job: {job_id}")
```

### 2. 마이그레이션 상세 정보 추가

```python
from modules.db_manager import add_migration_detail, update_migration_detail_status

# 상세 정보 생성
detail_id = add_migration_detail(
    job_id=1,
    table_name="users",
    delete_sql="DELETE FROM users WHERE id > 1000",
    insert_sql="INSERT INTO users SELECT * FROM source_db.users WHERE id > 1000"
)

# 실행 상태 업데이트 (성공)
update_migration_detail_status(
    detail_id=detail_id,
    status="success",
    affected_rows=500
)

# 실행 상태 업데이트 (실패)
update_migration_detail_status(
    detail_id=detail_id,
    status="failed",
    error_msg="Foreign key constraint violation"
)
```

### 3. 마이그레이션 작업 상태 조회

```python
from modules.db_manager import get_migration_job, get_migration_details

# 작업 조회
job = get_migration_job(1)
print(f"Job status: {job['status']}")

# 상세 정보 조회
details = get_migration_details(1)
for detail in details:
    print(f"{detail['table_name']}: {detail['execution_status']}")
```

### 4. 검증 결과 저장 및 조회

```python
from modules.db_manager import add_validation_result, get_validation_results

# 검증 결과 저장
add_validation_result(
    job_id=1,
    table_name="users",
    source_count=1000,
    target_count=1000,
    passed=True
)

# 검증 결과 조회
validations = get_validation_results(1)
for v in validations:
    status = "✓" if v['validation_passed'] else "✗"
    print(f"{status} {v['table_name']}: {v['source_count']} → {v['target_count']}")
```

### 5. 최근 작업 목록 조회

```python
from modules.db_manager import list_migration_jobs

jobs = list_migration_jobs(limit=10)
for job in jobs:
    print(f"{job['job_id']}: {job['status']} ({job['created_at']})")
```

## 워크플로우 예시

```
1. 사용자가 SQL 입력
   ↓
2. 테이블 추출 (page_3)
   ↓
3. create_migration_job() → job_id 생성
   ↓
4. 추출된 각 테이블에 대해:
   - add_migration_detail() → DELETE/INSERT SQL 생성 (추후 자동화)
   - SQL 실행
   - update_migration_detail_status() → 결과 저장
   ↓
5. 이관 검증:
   - add_validation_result() → 행 수 비교
   ↓
6. update_migration_job_status() → 작업 완료
```

## 주의사항

- **데이터베이스 파일**: `data_migration.db`는 `.gitignore`에 추가되어 있습니다. 
- **외래 키**: migration_details와 migration_validation은 migration_jobs의 job_id를 참조합니다.
- **JSON 저장**: extracted_tables는 JSON 형식으로 저장되므로, 조회 후 `json.loads()`로 파싱이 필요합니다.

## SQL 직접 쿼리

### 특정 작업의 모든 상세 정보 조회
```sql
SELECT md.*, mj.source_sql 
FROM migration_details md
JOIN migration_jobs mj ON md.job_id = mj.job_id
WHERE md.job_id = 1
ORDER BY md.detail_id;
```

### 이관 완료된 작업 조회
```sql
SELECT * FROM migration_jobs
WHERE status = 'completed'
ORDER BY created_at DESC;
```

### 실패한 이관 조회
```sql
SELECT * FROM migration_details
WHERE execution_status = 'failed'
ORDER BY executed_at DESC;
```

### 검증 실패한 테이블 조회
```sql
SELECT * FROM migration_validation
WHERE validation_passed = FALSE
ORDER BY validated_at DESC;
```

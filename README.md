# SQL 보조기 - 데이터 이관 도구

포트폴리오 데이터 마이그레이션을 위한 **LLM 기반 SQL 생성 및 실행 도구**입니다.  
Streamlit 기반의 직관적인 UI로 테이블 추출, SQL 자동 생성, 대량 실행을 한 번에 처리합니다.

## 🎯 주요 기능

### 1. **데이터 이관 도구** (Page 3)
사용자의 SQL 쿼리에서 테이블을 자동으로 추출하고, DELETE/INSERT 문을 AI가 생성하여 실행합니다.

**Workflow:**
1. **추출하기**: SQL 쿼리 → LLM이 참조 테이블 자동 추출
2. **작성하기**: 추출된 테이블 → SQL Generator가 DELETE/INSERT 자동 생성
3. **이관하기**: 사용자 검수 후 선택된 SQL 일괄 실행
4. **자동실행**: 추출 → 생성 → 실행을 한 번에 처리

**주요 특징:**
- ⚡ **실시간 진행 상황 표시**: 진행 바 + 현재 처리 중인 테이블명
- ✏️ **SQL 편집 기능**: 생성된 SQL을 화면에서 직접 수정 가능
- 🎯 **접미사 필터**: `_t` 등의 테이블 그룹으로 선택적 실행
- 📊 **통계 표시**: 성공/실패/영향받은 행 수 집계

### 2. **데이터 이관 확인** (Page 4)
원본 테이블과 이관 대상 테이블의 데이터를 양쪽에서 동시에 비교합니다.

**기능:**
- 원본 테이블(prod) vs 이관 테이블(test) 나란히 비교
- 필터링: 운용사코드, 펀드코드, 종목코드, 날짜 범위
- 통계: 데이터 건수 및 일치/불일치 상태 표시

### 3. **dbLink 주입기** (Page 2)
SQL 쿼리에 dbLink를 자동으로 주입합니다.

---

## 📋 설치 및 실행

### 요구사항
- Python 3.14+
- uv (또는 pip)
- OpenAI API Key (또는 호환 LLM)

### uv를 사용한 설치 (권장)

#### 1. uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 의존성 설치 및 환경 구성
```bash
uv sync
```
→ `.venv/` 자동 생성 + 모든 의존성 설치

#### 3. 환경변수 설정
`.streamlit/secretes.toml` 파일에 파일에 OpenAI API 키 설정:
OPENAI_API_KEY=sk-...
```

#### 4. 앱 실행
```bash
uv run streamlit run main.py
```

앱은 `http://localhost:8501`에서 시작됩니다.

---

### pip를 사용한 설치 (legacy)

#### 1. 가상환경 생성
```bash
python3.14 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate  # Windows
```

#### 2. 의존성 설치
```bash
pip install -e .
```

#### 3. 환경변수 설정
`.env` 파일에 OpenAI API 키 설정

#### 4. 앱 실행
```bash
streamlit run main.py
```

---

## 📁 프로젝트 구조

```
toy_2/
├── main.py                           # 메인 진입점 (페이지 네비게이션)
├── pyproject.toml                    # 프로젝트 메타데이터 + 의존성
├── uv.lock                           # 의존성 lock 파일 (uv)
├── .python-version                   # Python 3.14
├── data_migration.db                 # SQLite 데이터베이스
│
├── pages/
│   ├── page_2.py                    # dbLink 주입기
│   ├── page_3.py                    # 데이터 이관 도구 ⭐ 핵심
│   └── page_4.py                    # 데이터 이관 확인
│
├── modules/
│   ├── db/
│   │   ├── __init__.py
│   │   └── manager.py               # 데이터베이스 CRUD 작업
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── link_injector_adaptive.py    # dbLink 추출 (LangChain/LanGraph)
│   │   ├── link_injector_simple.py      # dbLink 수동 주입 (LangChain/LanGraph)
│   │   └── table_extractor.py           # 테이블 추출 (LangChain/LanGraph)
│   │
│   ├── sql/
│   │   ├── __init__.py
│   │   ├── generator.py              # DELETE/INSERT SQL 생성
│   │   └── executor.py               # SQLite 실행
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   └── link_validator.py         # 검증 함수들
│   │
│   └── sample_data.py                # 샘플 데이터 생성 (개발용)
│
└── style/
    ├── page_3.py                    # Page 3 CSS
    └── page_4.py                    # Page 4 CSS
```

### 모듈 구조 설명

| 디렉토리 | 용도 | 파일 |
|---------|------|------|
| **db/** | 데이터베이스 CRUD, 스키마 관리 | manager.py |
| **agents/** | LangGraph 워크플로우 (AI 에이전트) | link_injector_adaptive, link_injector_simple, table_extractor |
| **sql/** | SQL 생성·실행 (LLM 미사용 순수 로직) | generator.py, executor.py |
| **validation/** | 결과 검증 함수들 | link_validator.py |

---

## 🗄️ 데이터베이스 스키마

**SQLite 데이터베이스** (`data_migration.db`)

### 마이그레이션 추적 테이블
- `migration_jobs`: 마이그레이션 작업 레코드
- `migration_details`: SQL 실행 상세 (delete/insert, 상태, 영향받은 행)
- `migration_validation`: 마이그레이션 후 데이터 검증

### 소스 테이블 (prod)
- `pfo_stck_ma`: 포트폴리오 주식 마스터
- `pfo_fund_infr_ht`: 포트폴리오 펀드 정보 히스토리
- `pfo_fund_bs`: 포트폴리오 펀드 기본정보

### 타겟 테이블 (test, `_t` 접미사)
- `pfo_stck_ma_t`, `pfo_fund_infr_ht_t`, `pfo_fund_bs_t`

---

## 🚀 사용 예시

### 시나리오: 포트폴리오 데이터 마이그레이션

```sql
-- 1. Page 3에 입력
SELECT * FROM pfo_stck_ma 
WHERE mncm_code = 'E3069' AND proc_date BETWEEN '20260301' AND '20260430'
```

```
2. "추출하기" 클릭
   ↓ (테이블 추출 완료)
   pfo_stck_ma, pfo_fund_infr_ht 등이 자동으로 감지됨

3. "작성하기" 클릭
   ↓ (SQL 자동 생성)
   DELETE FROM pfo_stck_ma_t WHERE ...
   INSERT INTO pfo_stck_ma_t SELECT * FROM pfo_stck_ma WHERE ...

4. (선택) SQL 편집 후 "이관하기" 클릭
   ↓ (실시간 진행 상황 표시)
   처리 중 (1/5): pfo_stck_ma
   처리 중 (2/5): pfo_fund_infr_ht
   ...

5. Page 4에서 데이터 비교
   원본 테이블 [prod]  |  이관 테이블 [test]
   1,234건 조회됨      |  1,234건 조회됨 ✓ 일치
```

---

## 🔑 핵심 기술

| 컴포넌트 | 기술 | 역할 |
|---------|------|------|
| **Frontend** | Streamlit | 대화형 UI, 실시간 업데이트 |
| **Table Extraction** | LangChain + LanGraph | SQL 쿼리에서 테이블명 추출 |
| **SQL Generation** | Python + Jinja2 | WHERE 절 기반 DELETE/INSERT 자동 생성 |
| **Execution** | SQLite3 | 데이터베이스 실행 및 트랜잭션 관리 |
| **Styling** | Streamlit CSS  |

---

## 📊 성능

| 작업 | 소요 시간 |
|------|---------|
| 테이블 추출 (LLM call + verification ) | ~2초 |
| SQL 생성  | ~0초 |
| migration | 테이블 인덱스 및 데이터량에 따라 다름 |
---

## 🛠️ 커스터마이징

### 새로운 소스 테이블 추가
```python
# modules/db/manager.py
def get_source_tables():
    return ['pfo_stck_ma', 'pfo_fund_infr_ht', '새로운_테이블']
```

### WHERE 절 필터 추가
```python
# modules/sql/generator.py
def generate_sql_statements(...):
    # 새로운 조건 추가
    conditions.append(f"새로운_컬럼 = '{값}'")
```

### 테마 색상 변경
```python
# style/page_3.py
--shinhan-primary: #YourColor;  # 기본 색상 변경
```

### 새 의존성 추가 (uv 사용 시)
```bash
# 패키지 추가
uv add package_name

# 개발 전용 패키지 추가
uv add --group dev package_name

# 의존성 업데이트
uv sync
```

pyproject.toml의 `[project.dependencies]` 또는 `[project.optional-dependencies.dev]`에 자동으로 추가됩니다.

---

## 📝 세션 상태 관리

Page 3은 Streamlit 세션 상태를 통해 상태를 유지합니다:
- `result_df`: 추출된 테이블 목록
- `sql_statements`: 생성된 SQL 문
- `sql_edits`: 사용자 수정 사항
- `sql_selections`: 실행 선택 상태
- `auto_run_execute`: 자동실행 플래그

페이지를 벗어났다가 돌아와도 데이터가 유지됩니다.

---

## ⚠️ 주의사항

1. **데이터 손실 위험**: 실제 prod 데이터에 DELETE 실행 전에 반드시 백업하세요
2. **권한 확인**: 타겟 테이블에 INSERT 권한이 필요합니다
3. **API 비용**: LangChain은 OpenAI API를 호출하므로 비용이 발생할 수 있습니다
4. **데이터 검증**: Page 4에서 마이그레이션 후 데이터를 항상 확인하세요

---

## 📄 라이선스

MIT License

---

## 🤝 기여

이슈 및 Pull Request는 언제든 환영합니다!

---

**마지막 업데이트:** 2026-05-04 (uv 마이그레이션)

# SQL 보조기

Streamlit 기반의 SQL 쿼리 처리 및 분석 도구입니다.

## 주요 기능

### 1. dbLink 주입기 #1
- **설명**: 사용자의 요청 내용을 자동으로 분석하여 SQL 쿼리에 dbLink를 주입합니다.
- **사용 방법**:
  1. 쿼리 입력: SQL 쿼리를 왼쪽 텍스트 박스에 입력
  2. 요청 내용: 아래의 "요청내용" 필드에 원하는 작업을 기술
  3. "링크 주입하기" 버튼 클릭
  4. (선택) "검증하기" 버튼으로 변환 결과 검증

### 2. dbLink 주입기 #2
- **설명**: 사용자가 직접 입력한 dbLink를 SQL 쿼리에 주입합니다.
- **사용 방법**:
  1. 쿼리 입력: SQL 쿼리를 왼쪽 텍스트 박스에 입력
  2. dbLink 입력: "주입할 db link (1개)" 필드에 dbLink 입력
  3. "링크 주입하기" 버튼 클릭
  4. (선택) "검증하기" 버튼으로 변환 결과 검증

### 3. TABLE 추출기
- **설명**: SQL 쿼리에서 참조되는 모든 테이블 이름을 자동으로 추출합니다.
- **사용 방법**:
  1. 쿼리 입력: SQL 쿼리를 왼쪽 텍스트 박스에 입력
  2. "추출하기" 버튼 클릭
  3. 추출된 테이블 목록이 오른쪽에 표 형식으로 표시됨

## 설치 및 실행

### 요구사항
- Python 3.8 이상
- Streamlit

### 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
streamlit run main.py
```

## 프로젝트 구조

```
toy_2/
├── main.py                      # 메인 애플리케이션 진입점
├── css.py                       # CSS 스타일 적용
├── pages/
│   ├── page_1.py               # dbLink 주입기 #1
│   ├── page_2.py               # dbLink 주입기 #2
│   └── page_3.py               # TABLE 추출기
└── modules/
    ├── page_1/                 # 페이지 1 모듈
    │   ├── link_injector.py    # dbLink 추출 및 주입 로직
    │   └── funcs.py            # 검증 함수
    ├── page_2/                 # 페이지 2 모듈
    │   ├── link_injector.py    # dbLink 주입 로직
    │   └── funcs.py            # 검증 함수
    └── page_3/                 # 페이지 3 모듈
        └── table_extractor.py  # 테이블 추출 로직
```

## 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Model**: LangChain (그래프 기반 AI 워크플로우)

## 특징

- 🔗 자동 dbLink 추출 및 주입
- 📊 SQL 테이블 자동 추출
- ✅ 변환 결과 검증 기능
- 💻 직관적인 웹 UI
- 🔄 세션 기반 상태 관리

## 라이선스

MIT License

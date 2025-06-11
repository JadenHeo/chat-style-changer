# RAG API

Retrieval-Augmented Generation (RAG) 기반의 LLM API 서버입니다.

## 기능

- 문서 임베딩 및 저장
- 의미 기반 검색
- LLM을 활용한 질의응답

## 시작하기

### 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치

1. 저장소 클론
```bash
git clone [repository-url]
cd rag
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 필요한 환경 변수를 설정합니다:
```
OPENAI_API_KEY=your-api-key-here
```

### 실행

개발 서버 실행:
```bash
uvicorn app.main:app --reload
```

서버는 기본적으로 http://localhost:8000 에서 실행됩니다.

## API 문서

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
rag/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 애플리케이션
│   ├── config.py        # 설정 관리
│   ├── models/          # 데이터 모델
│   ├── services/        # 비즈니스 로직
│   └── api/            # API 엔드포인트
├── tests/              # 테스트 코드
├── .env               # 환경 변수
├── requirements.txt   # 의존성 목록
└── README.md         # 프로젝트 문서
```

## 라이선스

MIT License 
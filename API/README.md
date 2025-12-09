# KIS Stock Portfolio API

한국투자증권(KIS) Open API를 활용하여 개인의 주식 포트폴리오를 관리하고 기록하는 FastAPI 기반의 백엔드 서버입니다.

## 📌 주요 기능

1.  **사용자 인증 (Authentication)**
    *   회원가입 및 로그인 (JWT 기반 인증).
    *   다중 사용자 지원 (Multi-user).
2.  **한국투자증권 API 연동**
    *   API Key, Secret, 계좌번호 등록.
    *   실전/모의투자 환경 지원.
    *   접근 토큰(Access Token) 자동 발급 및 캐싱.
3.  **포트폴리오 동기화 (Sync)**
    *   증권사 계좌의 잔고를 가져와 DB에 저장.
    *   현재가, 평단가, 수익률 등 정보 갱신.
    *   `POST /api/v1/portfolio/sync` 엔드포인트를 통해 수동 동기화 가능.
4.  **주가 기록 및 스케줄러**
    *   **APScheduler**를 사용하여 주기적(기본 1시간)으로 모든 사용자의 포트폴리오를 동기화.
    *   갱신 시점의 주가(`StockPriceHistory`)를 기록하여 시계열 데이터 확보.
5.  **커스텀 메타데이터**
    *   각 종목에 대해 사용자가 직접 메모, 목표가, 태그 등을 설정 가능.

## 🛠 기술 스택

*   **Language**: Python 3.12+
*   **Web Framework**: FastAPI
*   **Database**: PostgreSQL
*   **ORM**: SQLAlchemy (Async)
*   **Authentication**: OAuth2 with Password (Bearer JWT), Passlib (Bcrypt)
*   **Scheduling**: APScheduler
*   **HTTP Client**: HTTPX (Async)

## 🚀 설치 및 실행 방법

### 1. 환경 변수 설정 (.env)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 설정하세요.

```ini
PROJECT_NAME="KIS Stock Portfolio"
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/kis_portfolio"
SECRET_KEY="your_super_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 준비

PostgreSQL 데이터베이스가 실행 중이어야 합니다. 테이블은 애플리케이션 시작 시 자동으로 생성됩니다.

### 4. 서버 실행

```bash
uvicorn main:app --reload
```

## 📚 API 명세 요약

서버 실행 후 `http://localhost:8000/docs`에서 Swagger UI를 통해 상세 API를 확인할 수 있습니다.

*   **Auth**
    *   `POST /api/v1/auth/signup`: 회원가입
    *   `POST /api/v1/auth/login`: 로그인 (Token 발급)
*   **Portfolio**
    *   `POST /api/v1/portfolio/keys`: KIS API Key 등록
    *   `POST /api/v1/portfolio/sync`: 포트폴리오 즉시 동기화
    *   `GET /api/v1/portfolio/holdings`: 보유 종목 및 커스텀 정보 조회
    *   `POST /api/v1/portfolio/stocks/{code}/meta`: 종목 메모/목표가 수정

## 📁 프로젝트 구조

```
app/
├── api/
│   └── v1/          # API 엔드포인트 (Auth, Portfolio)
├── core/            # 설정, 보안, 스케줄러
├── db/              # DB 연결 및 세션
├── models/          # SQLAlchemy 모델 정의
├── services/        # 비즈니스 로직 (동기화 등)
└── utils/           # 유틸리티 (KIS API 클라이언트)
```

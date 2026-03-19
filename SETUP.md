# TaskFlow - 설정 및 사용 가이드

## 프로젝트 소개

AI 기반 프로젝트 관리 도구로, Gemini AI가 프로젝트 목표를 분석하여 작업을 자동으로 분해하고 팀원에게 최적으로 배분해주는 서비스입니다.

---

## 필요한 API 키 / 환경변수 목록

| 변수명 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | https://aistudio.google.com/app/apikey |
| `SECRET_KEY` | JWT 서명용 비밀 키 | 직접 생성 (예: `openssl rand -hex 32`) |
| `STRIPE_SECRET_KEY` | Stripe 결제 비밀 키 | https://dashboard.stripe.com/apikeys |
| `STRIPE_WEBHOOK_SECRET` | Stripe 웹훅 서명 검증 키 | https://dashboard.stripe.com/webhooks |
| `PREMIUM_PRICE_ID` | Stripe 프리미엄 플랜 가격 ID | https://dashboard.stripe.com/products |
| `DATABASE_URL` | 데이터베이스 연결 URL (기본: SQLite) | - |

---

## GitHub Secrets 설정 방법

저장소 페이지 > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

| Secret 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio에서 발급한 키 |
| `SECRET_KEY` | 프로덕션용 JWT 비밀 키 |
| `STRIPE_SECRET_KEY` | Stripe 대시보드 비밀 키 |
| `STRIPE_WEBHOOK_SECRET` | Stripe 웹훅 시크릿 |
| `PREMIUM_PRICE_ID` | Stripe 가격 ID (price_xxx 형식) |

---

## 로컬 개발 환경 설정

### 1. `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./taskflow.db
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
PREMIUM_PRICE_ID=price_xxx
DEBUG=false
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

---

## 실행 방법

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI를 확인할 수 있습니다.

### Docker로 실행

```bash
docker-compose up --build
```

---

## API 엔드포인트 주요 사용법

### 헬스 체크

```
GET /health
```

### 회원가입

```
POST /api/users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword",
  "full_name": "홍길동",
  "skills": "Python, FastAPI, React"
}
```

### 로그인 (JWT 토큰 발급)

```
POST /api/users/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

응답으로 받은 `access_token`을 이후 요청의 `Authorization: Bearer <token>` 헤더에 포함합니다.

### 프로젝트 생성 (AI 작업 자동 분해)

```
POST /api/projects/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "쇼핑몰 웹사이트 개발",
  "description": "React 프론트엔드 + FastAPI 백엔드로 구성된 쇼핑몰",
  "deadline": "2025-06-30T00:00:00"
}
```

### 프로젝트 목록 조회

```
GET /api/projects/
Authorization: Bearer <access_token>
```

### 작업(Task) 목록 조회

```
GET /api/tasks/?project_id={project_id}
Authorization: Bearer <access_token>
```

### 작업 상태 업데이트

```
PATCH /api/tasks/{task_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "in_progress"
}
```

### 결제 체크아웃 세션 생성 (Stripe)

```
POST /api/payments/checkout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan": "premium"
}
```

---

전체 API 문서: http://localhost:8000/docs

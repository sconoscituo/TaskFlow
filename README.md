# TaskFlow

AI 프로젝트 관리 + 자동 작업 분배 도구

## 주요 기능

- Gemini AI로 프로젝트 목표 입력 → 작업(Task) 자동 분해
- 팀원 스킬 기반 작업 자동 배분 추천
- 진행률 추적 + AI 병목 감지 및 해결책 제안
- JWT 인증 + 프리미엄 플랜

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy (async), aiosqlite
- **AI**: Google Gemini 1.5 Flash
- **Auth**: JWT (python-jose)
- **Payment**: Stripe

## 시작하기

```bash
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 등 설정

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up --build
```

## API 문서

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI 확인

## 주요 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/users/register | 회원가입 |
| POST | /api/users/login | 로그인 |
| POST | /api/projects/ | 프로젝트 생성 |
| POST | /api/projects/{id}/decompose | AI 작업 자동 분해 |
| GET  | /api/projects/{id}/bottleneck | AI 병목 감지 |
| POST | /api/tasks/{id}/assign | AI 작업 자동 배분 |

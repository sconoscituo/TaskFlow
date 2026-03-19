from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import users, projects, tasks, payments
from app.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="AI 프로젝트 관리 + 자동 작업 분배 도구",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(payments.router)


@app.get("/")
async def root():
    return {"app": config.APP_NAME, "version": config.APP_VERSION, "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

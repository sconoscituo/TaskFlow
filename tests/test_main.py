import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "TaskFlow"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post("/api/users/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "skills": "Python, FastAPI"
        })
        assert reg.status_code == 201
        assert reg.json()["email"] == "test@example.com"

        login = await client.post("/api/users/login", data={
            "username": "test@example.com",
            "password": "testpass123"
        })
        assert login.status_code == 200
        assert "access_token" in login.json()

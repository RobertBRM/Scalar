
import pytest
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.user import router


@pytest.fixture
def valid_user():
    return {
        "email": "test@example.com",
        "password_hash": "demo-hash-not-a-real-password"
    }


@pytest.fixture
def saved_user(valid_user):
    return {
        "id": 1,
        **valid_user,
        "created_at": datetime(
            2026, 11, 14, 12, 0,
            tzinfo=timezone.utc
        )
    }


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as test_client:
        yield test_client


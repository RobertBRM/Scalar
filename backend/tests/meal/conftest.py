
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.routers.meal import router as meal_router


@pytest.fixture
def valid_meal():
    return {
        "user_id": 1,
        "meal_type": "breakfast",
        "notes": "Morning meal"
    }


@pytest.fixture
def saved_meal(valid_meal):
    return {
        "id": 10,
        **valid_meal,
        "logged_at": datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
    }


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(meal_router)

    with TestClient(app) as test_client:
        yield test_client

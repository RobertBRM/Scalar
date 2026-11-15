
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.user_profile import router


@pytest.fixture
def valid_profile():
    return {
        "user_id": 1,
        "display_name": "Test User",
        "date_of_birth": "2002-05-15",
        "height_cm": 175.5,
        "weight_kg": 75.0,
        "activity_level": "moderate"
    }


@pytest.fixture
def saved_profile(valid_profile):
    return {
        "id": 10,
        **valid_profile
    }


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as test_client:
        yield test_client


import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.nutrition_goal import router


@pytest.fixture
def valid_goal():
    return {
        "user_id": 1,
        "calorie_goal": 2200,
        "protein_goal_g": 150,
        "carb_goal_g": 250,
        "fat_goal_g": 70,
        "water_goal_ml": 2500
    }


@pytest.fixture
def saved_goal(valid_goal):
    return {
        "id": 10,
        **valid_goal
    }


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as test_client:
        yield test_client

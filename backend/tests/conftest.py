
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.food import router as food_router


@pytest.fixture
def valid_food():
    return {
        "name": "Eggs",
        "brand": "Generic",
        "serving_size": 100,
        "serving_unit": "g",
        "calories": 155,
        "protein_g": 13,
        "carbs_g": 1.1,
        "fat_g": 11,
        "fiber_g": 0
    }


@pytest.fixture
def saved_food(valid_food):
    return {
        "id": 1,
        **valid_food
    }


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(food_router)

    with TestClient(app) as test_client:
        yield test_client



import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.meal_item import router


@pytest.fixture
def valid_meal_item():
    return {
        "meal_id": 10,
        "food_id": 5,
        "quantity": 2
    }


@pytest.fixture
def saved_meal_item(valid_meal_item):
    return {
        "id": 20,
        **valid_meal_item
    }


@pytest.fixture
def saved_food():
    return {
        "id": 5,
        "name": "Eggs",
        "calories": 140,
        "protein_g": 12,
        "carbs_g": 2,
        "fat_g": 10
    }


@pytest.fixture
def saved_meal():
    return {
        "id": 10,
        "user_id": 1,
        "meal_type": "breakfast"
    }


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as test_client:
        yield test_client

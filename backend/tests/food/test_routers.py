
import pytest

from fastapi import HTTPException
from app.services import food_service


def test_create_food(
    client, monkeypatch, valid_food, saved_food
):
    monkeypatch.setattr(
        food_service,
        "create_food",
        lambda food: saved_food
    )

    response = client.post("/foods/", json=valid_food)

    assert response.status_code == 201
    assert response.json()["name"] == "Eggs"


def test_create_food_invalid(client, valid_food):
    valid_food["calories"] = -100

    response = client.post("/foods/", json=valid_food)

    assert response.status_code == 422


def test_get_all_foods(client, monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service,
        "get_all_foods",
        lambda: [saved_food]
    )

    response = client.get("/foods/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_foods(client, monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service,
        "search_foods",
        lambda name: [saved_food]
    )

    response = client.get(
        "/foods/search",
        params={"name": "Egg"}
    )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Eggs"


def test_get_food(client, monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service,
        "get_food",
        lambda food_id: saved_food
    )

    response = client.get("/foods/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_food_not_found(client, monkeypatch):
    def fake_get(food_id):
        raise HTTPException(
            status_code=404,
            detail="Food not found"
        )

    monkeypatch.setattr(
        food_service,
        "get_food",
        fake_get
    )

    response = client.get("/foods/999")

    assert response.status_code == 404


def test_update_food(client, monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service,
        "update_food",
        lambda food_id, food: {
            **saved_food,
            "calories": 200
        }
    )

    response = client.patch(
        "/foods/1",
        json={"calories": 200}
    )

    assert response.status_code == 200
    assert response.json()["calories"] == 200


def test_delete_food(client, monkeypatch):
    monkeypatch.setattr(
        food_service,
        "delete_food",
        lambda food_id: {"id": food_id}
    )

    response = client.delete("/foods/1")

    assert response.status_code == 204


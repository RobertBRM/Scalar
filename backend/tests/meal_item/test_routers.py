
from fastapi import HTTPException

from app.services import meal_item_service


def test_create_meal_item(
    client, monkeypatch,
    valid_meal_item, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service,
        "create_meal_item",
        lambda item: saved_meal_item
    )

    response = client.post(
        "/meal-items/",
        json=valid_meal_item
    )

    assert response.status_code == 201
    assert response.json()["id"] == 20


def test_create_invalid_quantity(
    client, valid_meal_item
):
    valid_meal_item["quantity"] = -1

    response = client.post(
        "/meal-items/",
        json=valid_meal_item
    )

    assert response.status_code == 422


def test_create_missing_food_id(
    client, valid_meal_item
):
    del valid_meal_item["food_id"]

    response = client.post(
        "/meal-items/",
        json=valid_meal_item
    )

    assert response.status_code == 422


def test_get_meal_item(
    client, monkeypatch, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service,
        "get_meal_item",
        lambda item_id: saved_meal_item
    )

    response = client.get("/meal-items/20")

    assert response.status_code == 200
    assert response.json()["id"] == 20


def test_get_meal_item_not_found(
    client, monkeypatch
):
    def fake_get(item_id):
        raise HTTPException(
            status_code=404,
            detail="Meal item not found"
        )

    monkeypatch.setattr(
        meal_item_service,
        "get_meal_item",
        fake_get
    )

    response = client.get("/meal-items/999")

    assert response.status_code == 404


def test_get_meal_items(
    client, monkeypatch, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service,
        "get_meal_items",
        lambda meal_id: [saved_meal_item]
    )

    response = client.get("/meal-items/meal/10")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_empty_meal_items(client, monkeypatch):
    monkeypatch.setattr(
        meal_item_service,
        "get_meal_items",
        lambda meal_id: []
    )

    response = client.get("/meal-items/meal/10")

    assert response.status_code == 200
    assert response.json() == []


def test_update_meal_item(
    client, monkeypatch, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service,
        "update_meal_item",
        lambda item_id, data: {
            **saved_meal_item,
            "quantity": 3
        }
    )

    response = client.patch(
        "/meal-items/20",
        json={"quantity": 3}
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 3


def test_delete_meal_item(client, monkeypatch):
    monkeypatch.setattr(
        meal_item_service,
        "delete_meal_item",
        lambda item_id: {"id": item_id}
    )

    response = client.delete("/meal-items/20")

    assert response.status_code == 204


def test_get_meal_nutrition(client, monkeypatch):
    monkeypatch.setattr(
        meal_item_service,
        "calculate_meal_nutrition",
        lambda meal_id: {
            "calories": 360,
            "protein_g": 28,
            "carbs_g": 19,
            "fat_g": 22
        }
    )

    response = client.get(
        "/meal-items/meal/10/nutrition"
    )

    assert response.status_code == 200
    assert response.json()["calories"] == 360
    assert response.json()["protein_g"] == 28


def test_invalid_item_id(client):
    response = client.get(
        "/meal-items/not-a-number"
    )

    assert response.status_code == 422

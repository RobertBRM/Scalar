
from fastapi import HTTPException

from app.services import meal_service


def test_create_meal(
    client, monkeypatch, valid_meal, saved_meal
):
    monkeypatch.setattr(
        meal_service,
        "create_meal",
        lambda meal: saved_meal
    )

    response = client.post(
        "/meals/",
        json=valid_meal
    )

    assert response.status_code == 201
    assert response.json()["id"] == 10


def test_create_meal_invalid_user(client, valid_meal):
    valid_meal["user_id"] = -1

    response = client.post(
        "/meals/",
        json=valid_meal
    )

    assert response.status_code == 422


def test_get_meal(client, monkeypatch, saved_meal):
    monkeypatch.setattr(
        meal_service,
        "get_meal",
        lambda meal_id: saved_meal
    )

    response = client.get("/meals/10")

    assert response.status_code == 200
    assert response.json()["id"] == 10


def test_get_meal_not_found(client, monkeypatch):
    def fake_get(meal_id):
        raise HTTPException(
            status_code=404,
            detail="Meal not found"
        )

    monkeypatch.setattr(
        meal_service,
        "get_meal",
        fake_get
    )

    response = client.get("/meals/999")

    assert response.status_code == 404


def test_get_user_meals(
    client, monkeypatch, saved_meal
):
    monkeypatch.setattr(
        meal_service,
        "get_user_meals",
        lambda user_id: [saved_meal]
    )

    response = client.get("/meals/user/1")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_meal(
    client, monkeypatch, saved_meal
):
    monkeypatch.setattr(
        meal_service,
        "update_meal",
        lambda meal_id, meal: {
            **saved_meal,
            "meal_type": "lunch"
        }
    )

    response = client.patch(
        "/meals/10",
        json={"meal_type": "lunch"}
    )

    assert response.status_code == 200
    assert response.json()["meal_type"] == "lunch"


def test_delete_meal(client, monkeypatch):
    monkeypatch.setattr(
        meal_service,
        "delete_meal",
        lambda meal_id: {"id": meal_id}
    )

    response = client.delete("/meals/10")

    assert response.status_code == 204


def test_invalid_meal_id(client):
    response = client.get("/meals/not-a-number")

    assert response.status_code == 422


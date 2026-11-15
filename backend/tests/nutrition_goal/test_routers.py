
from fastapi import HTTPException

from app.services import nutrition_goal_service


def test_create_goal(
    client, monkeypatch, valid_goal, saved_goal
):
    monkeypatch.setattr(
        nutrition_goal_service,
        "create_nutrition_goal",
        lambda goal: saved_goal
    )

    response = client.post(
        "/nutrition-goals/",
        json=valid_goal
    )

    assert response.status_code == 201
    assert response.json()["id"] == 10


def test_create_invalid_goal(client, valid_goal):
    valid_goal["calorie_goal"] = -100

    response = client.post(
        "/nutrition-goals/",
        json=valid_goal
    )

    assert response.status_code == 422


def test_create_missing_user(client, valid_goal):
    del valid_goal["user_id"]

    response = client.post(
        "/nutrition-goals/",
        json=valid_goal
    )

    assert response.status_code == 422


def test_get_goal(client, monkeypatch, saved_goal):
    monkeypatch.setattr(
        nutrition_goal_service,
        "get_nutrition_goal",
        lambda user_id: saved_goal
    )

    response = client.get("/nutrition-goals/1")

    assert response.status_code == 200
    assert response.json()["calorie_goal"] == 2200


def test_get_goal_not_found(client, monkeypatch):
    def fake_get(user_id):
        raise HTTPException(
            status_code=404,
            detail="Nutrition goal not found"
        )

    monkeypatch.setattr(
        nutrition_goal_service,
        "get_nutrition_goal",
        fake_get
    )

    response = client.get("/nutrition-goals/999")

    assert response.status_code == 404


def test_update_goal(client, monkeypatch, saved_goal):
    monkeypatch.setattr(
        nutrition_goal_service,
        "update_nutrition_goal",
        lambda user_id, goal: {
            **saved_goal,
            "calorie_goal": 2500
        }
    )

    response = client.patch(
        "/nutrition-goals/1",
        json={"calorie_goal": 2500}
    )

    assert response.status_code == 200
    assert response.json()["calorie_goal"] == 2500


def test_update_invalid_goal(client):
    response = client.patch(
        "/nutrition-goals/1",
        json={"protein_goal_g": -50}
    )

    assert response.status_code == 422


def test_delete_goal(client, monkeypatch):
    monkeypatch.setattr(
        nutrition_goal_service,
        "delete_nutrition_goal",
        lambda user_id: {"id": 10}
    )

    response = client.delete("/nutrition-goals/1")

    assert response.status_code == 204


def test_invalid_user_id(client):
    response = client.get(
        "/nutrition-goals/not-a-number"
    )

    assert response.status_code == 422


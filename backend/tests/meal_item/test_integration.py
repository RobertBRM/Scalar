
import os
from uuid import uuid4

import psycopg
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.meal_item import router

from app.repositories import (
    meal_repository,
    food_repository,
    meal_item_repository
)


pytestmark = pytest.mark.integration


@pytest.fixture
def integration_environment(monkeypatch):
    test_url = os.getenv("TEST_DATABASE_URL")
    app_url = os.getenv("DATABASE_URL")

    if not test_url:
        pytest.skip("TEST_DATABASE_URL not configured")

    if app_url and test_url == app_url:
        pytest.fail("Test database must be separate")

    if os.getenv("ALLOW_TEST_DB_WRITES") != "yes":
        pytest.skip("Test database writes not enabled")

    conn = psycopg.connect(test_url)

    # Repositories must share the same transaction
    # so all test records can be rolled back.
    class SharedConnection:
        def __enter__(self):
            return conn

        def __exit__(self, exc_type, exc, tb):
            return False

    for repository in (
        meal_repository,
        food_repository,
        meal_item_repository
    ):
        monkeypatch.setattr(
            repository,
            "get_connection",
            lambda: SharedConnection()
        )

    # Seed records in the test database.
    # Adjust columns to your actual schema.
    try:
        user = conn.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (%s, %s)
            RETURNING id
            """,
            (
                f"test-{uuid4()}@example.invalid",
                "test-only-hash"
            )
        ).fetchone()

        user_id = user[0]

        food = conn.execute(
            """
            INSERT INTO foods (
                name, calories, protein_g,
                carbs_g, fat_g
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            ("Test Eggs", 140, 12, 2, 10)
        ).fetchone()

        food_id = food[0]

        meal = conn.execute(
            """
            INSERT INTO meals (
                user_id, meal_type, notes
            )
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user_id, "breakfast", "Test meal")
        ).fetchone()

        meal_id = meal[0]

        app = FastAPI()
        app.include_router(router)

        with TestClient(app) as client:
            yield client, meal_id, food_id

    finally:
        conn.rollback()
        conn.close()


def test_meal_item_lifecycle(integration_environment):
    client, meal_id, food_id = integration_environment

    # Create
    created = client.post(
        "/meal-items/",
        json={
            "meal_id": meal_id,
            "food_id": food_id,
            "quantity": 2
        }
    )

    assert created.status_code == 201, created.text

    item_id = created.json()["id"]

    # Read
    fetched = client.get(f"/meal-items/{item_id}")

    assert fetched.status_code == 200
    assert fetched.json()["food_id"] == food_id

    # List items for meal
    items = client.get(
        f"/meal-items/meal/{meal_id}"
    )

    assert items.status_code == 200
    assert any(
        item["id"] == item_id
        for item in items.json()
    )

    # Update quantity
    updated = client.patch(
        f"/meal-items/{item_id}",
        json={"quantity": 3}
    )

    assert updated.status_code == 200
    assert float(updated.json()["quantity"]) == 3

    # Calculate nutrition
    nutrition = client.get(
        f"/meal-items/meal/{meal_id}/nutrition"
    )

    assert nutrition.status_code == 200
    assert float(nutrition.json()["calories"]) == 420
    assert float(nutrition.json()["protein_g"]) == 36

    # Delete
    deleted = client.delete(
        f"/meal-items/{item_id}"
    )

    assert deleted.status_code == 204

    # Verify deletion
    missing = client.get(
        f"/meal-items/{item_id}"
    )

    assert missing.status_code == 404

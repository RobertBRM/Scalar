
import os

import psycopg
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.meal import router
from app.repositories import (
    meal_repository,
    user_repository
)


pytestmark = pytest.mark.integration


@pytest.fixture
def integration_environment(monkeypatch):
    test_url = os.getenv("TEST_DATABASE_URL")
    app_url = os.getenv("DATABASE_URL")

    if not test_url:
        pytest.skip("TEST_DATABASE_URL not configured")

    if app_url and test_url == app_url:
        pytest.fail("Refusing to use application database")

    # Only enable this test against an isolated
    # database containing the application schema.
    if os.getenv("ALLOW_TEST_DB_WRITES") != "yes":
        pytest.skip("Test database writes not enabled")

    conn = psycopg.connect(test_url)

    class SharedConnection:
        def __enter__(self):
            return conn

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        meal_repository,
        "get_connection",
        lambda: SharedConnection()
    )

    monkeypatch.setattr(
        user_repository,
        "get_connection",
        lambda: SharedConnection()
    )

    app = FastAPI()
    app.include_router(router)

    try:
        with TestClient(app) as client:
            yield client, conn
    finally:
        conn.rollback()
        conn.close()


def test_meal_lifecycle(integration_environment):
    client, conn = integration_environment

    # Assumes the users table has these columns.
    user = conn.execute(
        """
        INSERT INTO users (email, password_hash)
        VALUES (%s, %s)
        RETURNING id
        """,
        ("meal-test@example.invalid", "test-only-hash")
    ).fetchone()

    user_id = user[0]

    # Create
    created = client.post(
        "/meals/",
        json={
            "user_id": user_id,
            "meal_type": "breakfast",
            "notes": "Integration test"
        }
    )

    assert created.status_code == 201, created.text

    meal_id = created.json()["id"]

    # Read
    fetched = client.get(f"/meals/{meal_id}")

    assert fetched.status_code == 200
    assert fetched.json()["user_id"] == user_id

    # List
    history = client.get(f"/meals/user/{user_id}")

    assert history.status_code == 200
    assert any(
        meal["id"] == meal_id
        for meal in history.json()
    )

    # Update
    updated = client.patch(
        f"/meals/{meal_id}",
        json={"meal_type": "lunch"}
    )

    assert updated.status_code == 200
    assert updated.json()["meal_type"] == "lunch"

    # Delete
    deleted = client.delete(f"/meals/{meal_id}")

    assert deleted.status_code == 204

    # Confirm deletion
    missing = client.get(f"/meals/{meal_id}")

    assert missing.status_code == 404


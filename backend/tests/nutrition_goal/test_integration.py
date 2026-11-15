
import os
from uuid import uuid4

import psycopg
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.nutrition_goal import router
from app.repositories import (
    nutrition_goal_repository,
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
        pytest.fail("Test database must be separate")

    if os.getenv("ALLOW_TEST_DB_WRITES") != "yes":
        pytest.skip("Test database writes not enabled")

    # Only use a verified, disposable test database.
    conn = psycopg.connect(test_url)

    class SharedConnection:
        def __enter__(self):
            return conn

        def __exit__(self, exc_type, exc, tb):
            return False

    for repository in (
        nutrition_goal_repository,
        user_repository
    ):
        monkeypatch.setattr(
            repository,
            "get_connection",
            lambda: SharedConnection()
        )

    try:
        user = conn.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (%s, %s)
            RETURNING id
            """,
            (
                f"goal-test-{uuid4()}@example.invalid",
                "test-only-hash"
            )
        ).fetchone()

        user_id = user[0]

        app = FastAPI()
        app.include_router(router)

        with TestClient(app) as client:
            yield client, user_id

    finally:
        conn.rollback()
        conn.close()


def test_goal_lifecycle(integration_environment):
    client, user_id = integration_environment

    goal_data = {
        "user_id": user_id,
        "calorie_goal": 2200,
        "protein_goal_g": 150,
        "carb_goal_g": 250,
        "fat_goal_g": 70,
        "water_goal_ml": 2500
    }

    # Create
    created = client.post(
        "/nutrition-goals/",
        json=goal_data
    )

    assert created.status_code == 201, created.text
    assert created.json()["user_id"] == user_id

    # Read
    fetched = client.get(
        f"/nutrition-goals/{user_id}"
    )

    assert fetched.status_code == 200
    assert fetched.json()["calorie_goal"] == 2200

    # Update
    updated = client.patch(
        f"/nutrition-goals/{user_id}",
        json={
            "calorie_goal": 2500,
            "protein_goal_g": 180
        }
    )

    assert updated.status_code == 200
    assert updated.json()["calorie_goal"] == 2500
    assert float(
        updated.json()["protein_goal_g"]
    ) == 180

    # Delete
    deleted = client.delete(
        f"/nutrition-goals/{user_id}"
    )

    assert deleted.status_code == 204

    # Verify deletion
    missing = client.get(
        f"/nutrition-goals/{user_id}"
    )

    assert missing.status_code == 404


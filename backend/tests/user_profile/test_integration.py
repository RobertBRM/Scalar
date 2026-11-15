
import os
from uuid import uuid4

import psycopg
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.user_profile import router
from app.repositories import (
    user_repository,
    user_profile_repository
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

    # Confirm this is a disposable database
    # before enabling integration tests.
    conn = psycopg.connect(test_url)

    class SharedConnection:
        def __enter__(self):
            return conn

        def __exit__(self, exc_type, exc, tb):
            return False

    for repository in (
        user_repository,
        user_profile_repository
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
                f"profile-test-{uuid4()}@example.invalid",
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


def test_profile_lifecycle(integration_environment):
    client, user_id = integration_environment

    profile_data = {
        "user_id": user_id,
        "display_name": "Test User",
        "date_of_birth": "2002-05-15",
        "height_cm": 175.5,
        "weight_kg": 75,
        "activity_level": "moderate"
    }

    # Create
    created = client.post(
        "/user-profiles/",
        json=profile_data
    )

    assert created.status_code == 201, created.text
    assert created.json()["user_id"] == user_id

    # Read
    fetched = client.get(
        f"/user-profiles/{user_id}"
    )

    assert fetched.status_code == 200
    assert fetched.json()["display_name"] == "Test User"

    # Update
    updated = client.patch(
        f"/user-profiles/{user_id}",
        json={
            "weight_kg": 80,
            "activity_level": "active"
        }
    )

    assert updated.status_code == 200
    assert float(updated.json()["weight_kg"]) == 80
    assert updated.json()["activity_level"] == "active"

    # Delete
    deleted = client.delete(
        f"/user-profiles/{user_id}"
    )

    assert deleted.status_code == 204

    # Verify deletion
    missing = client.get(
        f"/user-profiles/{user_id}"
    )

    assert missing.status_code == 404


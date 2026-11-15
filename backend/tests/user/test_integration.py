
import os
from uuid import uuid4

import psycopg
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.user import router
from app.repositories import user_repository


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

    # Must be a verified, disposable database.
    conn = psycopg.connect(test_url)

    class SharedConnection:
        def __enter__(self):
            return conn

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        user_repository,
        "get_connection",
        lambda: SharedConnection()
    )

    app = FastAPI()
    app.include_router(router)

    try:
        with TestClient(app) as client:
            yield client
    finally:
        conn.rollback()
        conn.close()


def test_user_lifecycle(integration_environment):
    client = integration_environment

    email = f"test-{uuid4()}@example.invalid"

    # Create
    created = client.post(
        "/users/",
        json={
            "email": email,
            "password_hash": "test-only-hash"
        }
    )

    assert created.status_code == 201, created.text

    user_id = created.json()["id"]

    assert created.json()["email"] == email
    assert "password_hash" not in created.json()

    # Read
    fetched = client.get(f"/users/{user_id}")

    assert fetched.status_code == 200
    assert fetched.json()["email"] == email

    # Update
    new_email = f"updated-{uuid4()}@example.invalid"

    updated = client.patch(
        f"/users/{user_id}",
        json={"email": new_email}
    )

    assert updated.status_code == 200
    assert updated.json()["email"] == new_email

    # Delete
    deleted = client.delete(f"/users/{user_id}")

    assert deleted.status_code == 204

    # Verify deletion
    missing = client.get(f"/users/{user_id}")

    assert missing.status_code == 404


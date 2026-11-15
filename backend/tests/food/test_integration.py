
import os

import psycopg
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.food import router
from app.repositories import food_repository


pytestmark = pytest.mark.integration


@pytest.fixture
def integration_client(monkeypatch):
    test_url = os.getenv("TEST_DATABASE_URL")

    if not test_url:
        pytest.skip(
            "TEST_DATABASE_URL is not configured"
        )

    # Never run against the application database.
    if test_url == os.getenv("DATABASE_URL"):
        pytest.fail(
            "Test database must be separate"
        )

    # Use a dedicated connection for this test.
    conn = psycopg.connect(test_url)

    conn.execute("""
        CREATE TEMP TABLE foods (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            brand VARCHAR(100),
            serving_size NUMERIC(10,2),
            serving_unit VARCHAR(20),
            calories INT NOT NULL,
            protein_g NUMERIC(10,2) NOT NULL,
            carbs_g NUMERIC(10,2),
            fat_g NUMERIC(10,2),
            fiber_g NUMERIC(10,2)
        )
    """)

    # Repository calls use this connection, but its
    # normal context manager would commit/close it.
    # Wrap it so tests retain control of its lifetime.
    class TestConnection:
        def __enter__(self):
            return conn

        def __exit__(self, exc_type, exc, tb):
            if exc_type is not None:
                conn.rollback()
            return False

    monkeypatch.setattr(
        food_repository,
        "get_connection",
        lambda: TestConnection()
    )

    app = FastAPI()
    app.include_router(router)

    try:
        with TestClient(app) as client:
            yield client
    finally:
        conn.close()


def test_food_create_read_update_delete(
    integration_client
):
    client = integration_client

    # Create
    created = client.post(
        "/foods/",
        json={
            "name": "Eggs",
            "brand": "Generic",
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 155,
            "protein_g": 13,
            "carbs_g": 1.1,
            "fat_g": 11,
            "fiber_g": 0
        }
    )

    assert created.status_code == 201

    food_id = created.json()["id"]

    # Read
    fetched = client.get(f"/foods/{food_id}")

    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Eggs"

    # Update
    updated = client.patch(
        f"/foods/{food_id}",
        json={"calories": 200}
    )

    assert updated.status_code == 200
    assert updated.json()["calories"] == 200

    # Delete
    deleted = client.delete(f"/foods/{food_id}")

    assert deleted.status_code == 204

    # Verify deletion
    missing = client.get(f"/foods/{food_id}")

    assert missing.status_code == 404


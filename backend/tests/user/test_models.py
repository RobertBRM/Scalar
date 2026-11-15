
import pytest
from pydantic import ValidationError

from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)


def test_create_user_valid(valid_user):
    user = UserCreate(**valid_user)

    assert user.email == "test@example.com"


def test_create_user_missing_email(valid_user):
    del valid_user["email"]

    with pytest.raises(ValidationError):
        UserCreate(**valid_user)


def test_create_user_missing_password_hash(valid_user):
    del valid_user["password_hash"]

    with pytest.raises(ValidationError):
        UserCreate(**valid_user)


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "missing-at-sign.com",
        "@example.com",
        "test@",
        ""
    ]
)
def test_create_user_invalid_email(valid_user, email):
    valid_user["email"] = email

    with pytest.raises(ValidationError):
        UserCreate(**valid_user)


def test_create_user_extra_field(valid_user):
    valid_user["unknown_field"] = "invalid"

    with pytest.raises(ValidationError):
        UserCreate(**valid_user)


def test_update_user_partial():
    user = UserUpdate(email="new@example.com")

    assert user.model_dump(exclude_unset=True) == {
        "email": "new@example.com"
    }


def test_update_user_empty():
    user = UserUpdate()

    assert user.model_dump(exclude_unset=True) == {}


def test_update_user_invalid_email():
    with pytest.raises(ValidationError):
        UserUpdate(email="invalid")


def test_user_response(saved_user):
    user = UserResponse(**saved_user)

    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.created_at is not None


def test_user_response_excludes_password_hash(saved_user):
    user = UserResponse(**saved_user)

    result = user.model_dump()

    assert "password_hash" not in result


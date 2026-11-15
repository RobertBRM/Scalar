
import pytest
from pydantic import ValidationError

from app.models.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse
)


def test_create_profile_valid(valid_profile):
    profile = UserProfileCreate(**valid_profile)

    assert profile.user_id == 1
    assert profile.display_name == "Test User"
    assert profile.activity_level == "moderate"


def test_create_profile_missing_user(valid_profile):
    del valid_profile["user_id"]

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


@pytest.mark.parametrize("user_id", [0, -1])
def test_create_profile_invalid_user(
    valid_profile, user_id
):
    valid_profile["user_id"] = user_id

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


@pytest.mark.parametrize(
    "field,value",
    [
        ("height_cm", 0),
        ("height_cm", -10),
        ("weight_kg", 0),
        ("weight_kg", -10)
    ]
)
def test_create_profile_invalid_measurements(
    valid_profile, field, value
):
    valid_profile[field] = value

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


@pytest.mark.parametrize(
    "activity",
    ["inactive", "very_active", "unknown"]
)
def test_create_profile_invalid_activity(
    valid_profile, activity
):
    valid_profile["activity_level"] = activity

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


def test_create_profile_name_too_long(valid_profile):
    valid_profile["display_name"] = "A" * 21

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


def test_create_profile_invalid_date(valid_profile):
    valid_profile["date_of_birth"] = "not-a-date"

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


def test_create_profile_extra_field(valid_profile):
    valid_profile["unknown_field"] = "invalid"

    with pytest.raises(ValidationError):
        UserProfileCreate(**valid_profile)


def test_create_profile_optional_fields():
    profile = UserProfileCreate(user_id=1)

    assert profile.user_id == 1
    assert profile.display_name is None
    assert profile.height_cm is None


def test_update_profile_partial():
    profile = UserProfileUpdate(weight_kg=80)

    assert profile.model_dump(exclude_unset=True) == {
        "weight_kg": 80
    }


def test_update_profile_empty():
    profile = UserProfileUpdate()

    assert profile.model_dump(exclude_unset=True) == {}


def test_update_profile_invalid_activity():
    with pytest.raises(ValidationError):
        UserProfileUpdate(activity_level="invalid")


def test_profile_response(saved_profile):
    profile = UserProfileResponse(**saved_profile)

    assert profile.id == 10
    assert profile.user_id == 1
    assert profile.display_name == "Test User"


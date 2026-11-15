import logging
from datetime import datetime, timezone

from fastapi import HTTPException

from app.models.food import FoodCreate
from app.models.meal import MealCreate
from app.models.meal_item import MealItemCreate
from app.repositories import user_repository, food_repository, meal_repository, meal_item_repository

logger = logging.getLogger(__name__)


def save_scan(analysis: dict, user_id: int, meal_type: str):
    """Log one serving of the exact nutrition returned by the analyzer."""
    food_data = FoodCreate.model_validate(analysis)
    if user_repository.get_user_by_id(user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    food = meal = None
    try:
        food = food_repository.create_food(food_data)
        meal = meal_repository.create_meal(MealCreate(
            user_id=user_id,
            meal_type=meal_type,
            logged_at=datetime.now(timezone.utc),
            notes=food_data.name,
        ))
        item = meal_item_repository.create_meal_item(MealItemCreate(
            meal_id=meal["id"], food_id=food["id"], quantity=1,
        ))
        if not item:
            raise RuntimeError("Meal item was not saved")
    except Exception:
        # These REST writes cannot share a transaction. Remove partial records
        # in reverse order, and retain the food if deleting the meal fails.
        try:
            if meal:
                meal_repository.delete_meal(meal["id"])
            if food:
                food_repository.delete_food(food["id"])
        except Exception:
            logger.exception("Failed to clean up an incomplete food scan")
        raise

    return {"food_id": food["id"], "meal_id": meal["id"], "meal_item_id": item["id"]}

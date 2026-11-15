
from fastapi import APIRouter, status

from app.models.meal_item import (
    MealItemCreate,
    MealItemUpdate,
    MealItemResponse
)

from app.services import meal_item_service


router = APIRouter(
    prefix="/meal-items",
    tags=["Meal Items"]
)


@router.post(
    "/",
    response_model=MealItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meal_item(item: MealItemCreate):
    return meal_item_service.create_meal_item(item)


@router.get(
    "/meal/{meal_id}",
    response_model=list[MealItemResponse]
)
def get_meal_items(meal_id: int):
    return meal_item_service.get_meal_items(meal_id)


@router.get(
    "/meal/{meal_id}/nutrition"
)
def get_meal_nutrition(meal_id: int):
    return meal_item_service.calculate_meal_nutrition(
        meal_id
    )


@router.get("/meal/{meal_id}/foods")
def get_meal_foods(meal_id: int):
    return meal_item_service.get_meal_foods(meal_id)


@router.get(
    "/{item_id}",
    response_model=MealItemResponse
)
def get_meal_item(item_id: int):
    return meal_item_service.get_meal_item(item_id)


@router.patch(
    "/{item_id}",
    response_model=MealItemResponse
)
def update_meal_item(
    item_id: int,
    item: MealItemUpdate
):
    return meal_item_service.update_meal_item(
        item_id, item
    )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_meal_item(item_id: int):
    meal_item_service.delete_meal_item(item_id)


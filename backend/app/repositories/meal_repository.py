from app.database import get_supabase
from app.repositories._supabase_utils import first, serialize
from app.models.meal import MealCreate, MealUpdate


def create_meal(meal: MealCreate):
    data = meal.model_dump(exclude_unset=True)
    if data.get("logged_at") is None:
        data.pop("logged_at", None)
    response = get_supabase().table("meals").insert(serialize(data)).execute()
    return first(response)


def get_meal_by_id(meal_id: int):
    response = get_supabase().table("meals").select("*").eq("id", meal_id).limit(1).execute()
    return first(response)


def get_meals_by_user(user_id: int):
    response = (get_supabase().table("meals").select("*")
                .eq("user_id", user_id).order("logged_at", desc=True).execute())
    return response.data


def update_meal(meal_id: int, meal: MealUpdate):
    data = meal.model_dump(exclude_unset=True)
    if not data:
        return get_meal_by_id(meal_id)
    response = get_supabase().table("meals").update(serialize(data)).eq("id", meal_id).execute()
    return first(response)


def delete_meal(meal_id: int):
    response = get_supabase().table("meals").delete().eq("id", meal_id).execute()
    row = first(response)
    return {"id": row["id"]} if row else None

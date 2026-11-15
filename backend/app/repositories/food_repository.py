from app.database import get_supabase
from app.repositories._supabase_utils import first, serialize
from app.models.food import FoodCreate, FoodUpdate


def create_food(food: FoodCreate):
    response = get_supabase().table("foods").insert(serialize(food.model_dump())).execute()
    return first(response)


def get_food_by_id(food_id: int):
    response = get_supabase().table("foods").select("*").eq("id", food_id).limit(1).execute()
    return first(response)


def get_all_foods():
    response = get_supabase().table("foods").select("*").order("id").execute()
    return response.data


def search_foods(name: str):
    response = (get_supabase().table("foods").select("*")
                .ilike("name", f"%{name}%").order("name").limit(50).execute())
    return response.data


def update_food(food_id: int, food: FoodUpdate):
    data = food.model_dump(exclude_unset=True)
    if not data:
        return get_food_by_id(food_id)
    response = get_supabase().table("foods").update(serialize(data)).eq("id", food_id).execute()
    return first(response)


def delete_food(food_id: int):
    response = get_supabase().table("foods").delete().eq("id", food_id).execute()
    row = first(response)
    return {"id": row["id"]} if row else None

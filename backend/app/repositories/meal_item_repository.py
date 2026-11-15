from app.database import get_supabase
from app.repositories._supabase_utils import first, serialize
from app.models.meal_item import MealItemCreate, MealItemUpdate


def create_meal_item(item: MealItemCreate):
    response = get_supabase().table("meal_items").insert(serialize(item.model_dump())).execute()
    return first(response)


def get_meal_item_by_id(item_id: int):
    response = get_supabase().table("meal_items").select("*").eq("id", item_id).limit(1).execute()
    return first(response)


def get_items_by_meal(meal_id: int):
    response = (get_supabase().table("meal_items").select("*")
                .eq("meal_id", meal_id).order("id").execute())
    return response.data


def get_meal_food_details(meal_id: int):
    # Requires a foreign key from meal_items.food_id to foods.id.
    response = (get_supabase().table("meal_items")
                .select("id,meal_id,food_id,quantity,foods!inner(name,calories,protein_g,carbs_g,fat_g)")
                .eq("meal_id", meal_id).execute())
    results = []
    for row in response.data:
        food = row.get("foods") or {}
        results.append({
            "id": row["id"], "meal_id": row["meal_id"],
            "food_id": row["food_id"], "quantity": row["quantity"],
            "name": food.get("name"), "calories": food.get("calories"),
            "protein_g": food.get("protein_g"), "carbs_g": food.get("carbs_g"),
            "fat_g": food.get("fat_g"),
        })
    return results


def update_meal_item(item_id: int, item: MealItemUpdate):
    data = item.model_dump(exclude_unset=True)
    if not data:
        return get_meal_item_by_id(item_id)
    response = get_supabase().table("meal_items").update(serialize(data)).eq("id", item_id).execute()
    return first(response)


def delete_meal_item(item_id: int):
    response = get_supabase().table("meal_items").delete().eq("id", item_id).execute()
    row = first(response)
    return {"id": row["id"]} if row else None

from app.database import get_supabase
from app.repositories._supabase_utils import first, serialize
from datetime import datetime, timezone
from app.models.nutrition_goal import NutritionGoalCreate, NutritionGoalUpdate


def create_nutrition_goal(goal: NutritionGoalCreate):
    response = get_supabase().table("nutrition_goals").insert(serialize(goal.model_dump())).execute()
    return first(response)


def get_nutrition_goal_by_user_id(user_id: int):
    response = (get_supabase().table("nutrition_goals").select("*")
                .eq("user_id", user_id).limit(1).execute())
    return first(response)


def update_nutrition_goal(user_id: int, goal: NutritionGoalUpdate):
    data = goal.model_dump(exclude_unset=True)
    if not data:
        return get_nutrition_goal_by_user_id(user_id)
    # Original SQL always set updated_at = NOW() on updates.
    data["updated_at"] = datetime.now(timezone.utc)
    response = (get_supabase().table("nutrition_goals")
                .update(serialize(data)).eq("user_id", user_id).execute())
    return first(response)


def delete_nutrition_goal(user_id: int):
    response = get_supabase().table("nutrition_goals").delete().eq("user_id", user_id).execute()
    row = first(response)
    return {"id": row["id"]} if row else None

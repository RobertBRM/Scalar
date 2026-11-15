from app.database import get_supabase
from app.repositories._supabase_utils import first, serialize
from app.models.user_profile import UserProfileCreate, UserProfileUpdate


def create_profile(profile: UserProfileCreate):
    response = get_supabase().table("user_profiles").insert(serialize(profile.model_dump())).execute()
    return first(response)


def get_profile_by_user_id(user_id: int):
    response = (get_supabase().table("user_profiles").select("*")
                .eq("user_id", user_id).limit(1).execute())
    return first(response)


def update_profile(user_id: int, profile: UserProfileUpdate):
    data = profile.model_dump(exclude_unset=True)
    if not data:
        return get_profile_by_user_id(user_id)
    response = (get_supabase().table("user_profiles").update(serialize(data))
                .eq("user_id", user_id).execute())
    return first(response)


def delete_profile(user_id: int):
    response = get_supabase().table("user_profiles").delete().eq("user_id", user_id).execute()
    row = first(response)
    return {"id": row["id"]} if row else None

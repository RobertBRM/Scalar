from app.database import get_supabase
from app.repositories._supabase_utils import first, serialize
def create_user(email: str, password_hash: str):
    response = (get_supabase().table("users")
                .insert({"email": email, "password_hash": password_hash}).execute())
    row = first(response)
    return {k: row[k] for k in ("id", "email", "created_at")} if row else None


def get_user_by_id(user_id: int):
    response = (get_supabase().table("users").select("id,email,created_at")
                .eq("id", user_id).limit(1).execute())
    return first(response)


def get_user_by_email(email: str):
    # Internal authentication lookup; must remain backend-only.
    response = (get_supabase().table("users").select("*")
                .eq("email", email).limit(1).execute())
    return first(response)


def update_user(user_id: int, email: str | None = None,
                password_hash: str | None = None):
    updates = {}
    if email is not None:
        updates["email"] = email
    if password_hash is not None:
        updates["password_hash"] = password_hash
    if not updates:
        return get_user_by_id(user_id)
    response = (get_supabase().table("users").update(updates)
                .eq("id", user_id).execute())
    row = first(response)
    return {k: row[k] for k in ("id", "email", "created_at")} if row else None


def delete_user(user_id: int):
    response = get_supabase().table("users").delete().eq("id", user_id).execute()
    row = first(response)
    return {"id": row["id"]} if row else None

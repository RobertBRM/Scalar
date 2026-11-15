from app.database import get_supabase

def main():
    supabase = get_supabase()

    response = (
        supabase.table("foods")
        .select("id")
        .limit(1)
        .execute()
    )

    print("Supabase SELECT completed successfully.")
    print(f"Visible food rows returned: {len(response.data)}")

if __name__ == "__main__":
    main()
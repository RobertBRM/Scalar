from app.repositories.food_repository import get_all_foods

def main():
    foods = get_all_foods()

    print("Food repository connected successfully.")
    print("Foods returned:", foods)

if __name__ == "__main__":
    main()
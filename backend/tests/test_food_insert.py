from app.repositories.food_repository import create_food
from app.models.food import FoodCreate

def main():
    food = FoodCreate(
        name="Test Apple",
        brand=None,
        serving_size=100,
        serving_unit="g",
        calories=52,
        protein_g=0.3,
        carbs_g=14,
        fat_g=0.2,
        fiber_g=2.4
    )

    result = create_food(food)

    print("Food created successfully!")
    print(result)

if __name__ == "__main__":
    main()
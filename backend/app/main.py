
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.food import router as food_router
from app.routers.user import router as user_router
from app.routers.user_profile import router as user_profile_router
from app.routers.nutrition_goal import router as nutrition_goal_router
from app.routers.meal import router as meal_router
from app.routers.meal_item import router as meal_item_router
from app.routers.raspberry import router as raspberry_router

app = FastAPI(
    title="Daily Plate API",
    description="Nutrition tracking backend for Daily Plate",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(food_router)
app.include_router(user_router)
app.include_router(user_profile_router)
app.include_router(nutrition_goal_router)
app.include_router(meal_router)
app.include_router(meal_item_router)
app.include_router(raspberry_router)

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Daily Plate API is running",
        "status": "ok"
    }

@app.get("/api/test", tags=["Health"])
def test_connection():
    return {
        "status": "success",
        "message": "Frontend connected to backend!"
    }
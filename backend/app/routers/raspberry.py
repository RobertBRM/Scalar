from datetime import datetime
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from pathlib import Path
from uuid import uuid4
import logging
from starlette.concurrency import run_in_threadpool

from app.services.gemini_service import analyze_food
from app.services.scan_service import save_scan
from app.models.meal import MealType


router = APIRouter(
    prefix="/raspberry",
    tags=["Raspberry Pi"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_auto_meal_type() -> MealType:
    """Automatically assigns breakfast, lunch, dinner, or snack based on current hour."""
    hour = datetime.now().hour
    if 5 <= hour < 11:
        return "breakfast"
    elif 11 <= hour < 16:
        return "lunch"
    elif 16 <= hour < 22:
        return "dinner"
    return "snack"


@router.get("/health")
def check_connection():
    return {
        "status": "online",
        "message": "Raspberry Pi API is ready"
    }


@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    weight_category: str | None = Form(None),
    user_id: int = Form(1, gt=0),
    meal_type: MealType | None = Form(None)
):
    if image.content_type not in (
        "image/jpeg",
        "image/png"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported"
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Image cannot be empty"
        )

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds 10 MB limit"
        )

    # Save the uploaded picture
    extension = (
        ".jpg"
        if image.content_type == "image/jpeg"
        else ".png"
    )

    filename = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / filename

    file_path.write_bytes(image_bytes)

    # Analyze the food image
    try:
        analysis = await analyze_food(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            weight_category=weight_category
        )

    except Exception as error:
        print("Analysis failed:", repr(error))

        raise HTTPException(
            status_code=502,
            detail="Analysis failed"
        )

    # Do NOT save to database if the image could not be identified ("Unknown")
    food_name = str(analysis.get("name", "")).strip().lower()
    if food_name in {"", "unknown", "unidentified", "none", "null", "error"}:
        return {
            "status": "success",
            "filename": filename,
            "weight_category": weight_category,
            "analysis": analysis,
            "records": None
        }

    # Auto-select meal_type by time of day if not explicitly sent
    resolved_meal_type: MealType = meal_type if meal_type is not None else get_auto_meal_type()

    # Save valid food scan to database (never crash the Pi response if DB has an issue)
    records = None
    try:
        records = await run_in_threadpool(save_scan, analysis, user_id, resolved_meal_type)
    except Exception as error:
        logging.getLogger(__name__).exception(f"Could not persist Raspberry Pi scan: {error}")

    # Return JSON to Raspberry Pi
    return {
        "status": "success",
        "filename": filename,
        "weight_category": weight_category,
        "analysis": analysis,
        "records": records
    }
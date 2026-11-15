
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
from pydantic import ValidationError
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
    meal_type: MealType = Form("snack")
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

    # Send the picture to Gemini
    try:
        analysis = await analyze_food(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            weight_category=weight_category
        )

    except Exception as error:
        print("Gemini analysis failed:", repr(error))

        raise HTTPException(
            status_code=502,
            detail="Gemini analysis failed"
        )

    # Save before acknowledging success so the dashboard reads the same data.
    try:
        records = await run_in_threadpool(save_scan, analysis, user_id, meal_type)
    except HTTPException:
        raise
    except ValidationError as error:
        raise HTTPException(status_code=502, detail="Food analysis returned invalid nutrition data") from error
    except Exception as error:
        logging.getLogger(__name__).exception("Could not persist Raspberry Pi scan")
        raise HTTPException(status_code=503, detail="Could not save scan; please retry") from error

    # Return JSON to Raspberry Pi
    return {
        "status": "success",
        "filename": filename,
        "weight_category": weight_category,
        "analysis": analysis,
        "records": records
    }

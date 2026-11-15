
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from pathlib import Path
from uuid import uuid4

from app.services.gemini_service import analyze_food


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
    weight_category: str | None = Form(None)
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

    # Return JSON to Raspberry Pi
    return {
        "status": "success",
        "filename": filename,
        "weight_category": weight_category,
        "analysis": analysis
    }

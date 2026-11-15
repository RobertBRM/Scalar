
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

router = APIRouter(
    prefix="/raspberry",
    tags=["Raspberry Pi"]
)


@router.get("/health")
def check_connection():
    return {
        "status": "online",
        "message": "Raspberry Pi API is ready"
    }


@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    weight_category: Optional[str] = Form(None)
):
    # Validate image format
    if image.content_type not in [
        "image/jpeg",
        "image/png"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported"
        )

    # Read the uploaded image
    image_bytes = await image.read()

    # Prevent empty uploads
    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Image cannot be empty"
        )

    # Future: send image_bytes to an analysis service

    return {
        "status": "success",
        "filename": image.filename,
        "image_size_bytes": len(image_bytes),
        "weight_category": weight_category,
        "analysis": {
            "message": "Image received successfully"
        }
    }


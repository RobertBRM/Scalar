import io
import os
import re
import json
import base64
from PIL import Image
from dotenv import load_dotenv
from groq import AsyncGroq
from pydantic import BaseModel

load_dotenv()


class FoodAnalysis(BaseModel):
    name: str
    brand: str | None = None

    serving_size: float
    serving_unit: str

    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float | None = None


def get_failsafe_response():
    """Returned when the API fails or no food can be identified in the image."""
    return {
        "name": "Unknown",
        "brand": None,
        "serving_size": 100.0,
        "serving_unit": "g",
        "calories": 0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0
    }


def optimize_image_for_groq(image_bytes: bytes) -> str:
    """Resizes and compresses the image in memory for fast Groq processing."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((800, 800))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def extract_json_dict(raw_text: str) -> dict:
    """Safely extracts JSON from model output even if <think> tags or markdown exist."""
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return json.loads(cleaned)


async def analyze_food(
    image_bytes: bytes,
    mime_type: str,
    weight_category: str | None = None
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[Fail-Safe] GROQ_API_KEY is not configured in .env!")
        return get_failsafe_response()

    client = AsyncGroq(api_key=api_key)

    try:
        b64_image = optimize_image_for_groq(image_bytes)
    except Exception as img_err:
        print(f"[Fail-Safe] Image optimization failed, using raw bytes: {img_err}")
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """Identify the food, fruit, drink, or snack in this image.
If ANY food or fruit (like a banana, apple, snack, meal) is visible, provide its name and estimated nutrition per 100g.
Do NOT output any thinking or explanation. Output ONLY a raw JSON object with these exact keys:
{
  "name": "Banana",
  "brand": null,
  "serving_size": 100.0,
  "serving_unit": "g",
  "calories": 89,
  "protein_g": 1.1,
  "carbs_g": 22.8,
  "fat_g": 0.3,
  "fiber_g": 2.6
}"""

    # Try Qwen first, and fall back to Llama 4 Maverick if Qwen errors out
    vision_models = [
        "qwen/qwen3.8-27b",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
    ]

    for model_id in vision_models:
        try:
            print(f"[Groq] Sending image to {model_id}...")
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=512,
            )

            content = response.choices[0].message.content
            print(f"[Groq Raw Output ({model_id})]: {content}")

            if not content:
                continue

            data = extract_json_dict(content)

            food = FoodAnalysis(
                name=str(data.get("name") or "Unknown"),
                brand=data.get("brand"),
                serving_size=100.0,
                serving_unit="g",
                calories=max(0, int(round(float(data.get("calories") or 0)))),
                protein_g=max(0.0, float(data.get("protein_g") or 0.0)),
                carbs_g=max(0.0, float(data.get("carbs_g") or 0.0)),
                fat_g=max(0.0, float(data.get("fat_g") or 0.0)),
                fiber_g=max(0.0, float(data.get("fiber_g") or 0.0)),
            )

            return food.model_dump(mode="json")

        except Exception as error:
            print(f"[Groq Warning] {model_id} failed: {repr(error)}")

    print("[Fail-Safe] All vision models failed.")
    return get_failsafe_response()
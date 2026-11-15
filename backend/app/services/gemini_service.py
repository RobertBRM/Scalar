import os
import json
import base64
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


async def analyze_food(
    image_bytes: bytes,
    mime_type: str,
    weight_category: str | None = None
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[Fail-Safe] GROQ_API_KEY is not configured.")
        return get_failsafe_response()

    client = AsyncGroq(api_key=api_key)
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
    You are a food recognition and nutritional analysis system.
    Analyze the provided image and identify the food.

    If no food is visible or the image cannot be identified as food, set "name" to "Unknown" and all nutritional values to 0.

    Otherwise, estimate nutritional values for exactly 100 grams ("serving_size": 100.0, "serving_unit": "g").

    Return ONLY valid JSON matching this exact structure:
    {
      "name": "string",
      "brand": null,
      "serving_size": 100.0,
      "serving_unit": "g",
      "calories": 0,
      "protein_g": 0.0,
      "carbs_g": 0.0,
      "fat_g": 0.0,
      "fiber_g": 0.0
    }
    """

    try:
        response = await client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        content = response.choices[0].message.content
        if not content:
            return get_failsafe_response()

        data = json.loads(content)
        food = FoodAnalysis.model_validate(data)

        food.serving_size = 100.0
        food.serving_unit = "g"

        return food.model_dump(mode="json")

    except Exception as error:
        print(f"[Fail-Safe] Qwen analysis failed: {repr(error)}")
        return get_failsafe_response()
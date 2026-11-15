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
    """Extracts the JSON object from Qwen's response."""
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return json.loads(cleaned)


def parse_num(val, default=0.0) -> float:
    """Safely extracts a float even if the model returns strings like '22.8g' or '89 kcal'."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    match = re.search(r"[-+]?\d*\.?\d+", str(val))
    return float(match.group(0)) if match else default


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

    try:
        b64_image = optimize_image_for_groq(image_bytes)

        prompt = """You are a nutrition database.
1. Identify the food or fruit in this image.
2. Estimate its realistic USDA nutritional values per 100 grams.
3. CRITICAL: NEVER return 0 for calories, carbs_g, protein_g, or fat_g when a food is identified! Always provide realistic, non-zero nutritional estimates for that food.
4. Only set "name" to "Unknown" if there is no food in the image.

Respond with ONLY a valid JSON object (no thinking, no markdown) using these exact keys:
{
  "name": "<identified food name>",
  "brand": null,
  "serving_size": 100.0,
  "serving_unit": "g",
  "calories": <integer kcal per 100g>,
  "protein_g": <float grams protein per 100g>,
  "carbs_g": <float grams carbs per 100g>,
  "fat_g": <float grams fat per 100g>,
  "fiber_g": <float grams fiber per 100g>
}"""

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
        print(f"[Qwen Raw Output]: {content}")

        if not content:
            return get_failsafe_response()

        data = extract_json_dict(content)

        # Support alternative key names just in case Qwen omits '_g'
        cal = int(round(parse_num(data.get("calories") or data.get("kcal"), 0)))
        prot = parse_num(data.get("protein_g") or data.get("protein"), 0.0)
        carbs = parse_num(data.get("carbs_g") or data.get("carbs") or data.get("carbohydrates"), 0.0)
        fat = parse_num(data.get("fat_g") or data.get("fat"), 0.0)
        fiber = parse_num(data.get("fiber_g") or data.get("fiber"), 0.0)

        food = FoodAnalysis(
            name=str(data.get("name") or "Unknown").strip(),
            brand=data.get("brand"),
            serving_size=100.0,
            serving_unit="g",
            calories=max(0, cal),
            protein_g=round(max(0.0, prot), 1),
            carbs_g=round(max(0.0, carbs), 1),
            fat_g=round(max(0.0, fat), 1),
            fiber_g=round(max(0.0, fiber), 1),
        )

        return food.model_dump(mode="json")

    except Exception as error:
        print(f"[Fail-Safe] Qwen analysis failed: {repr(error)}")
        return get_failsafe_response()
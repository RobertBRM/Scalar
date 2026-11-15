
import os
import json

from decimal import Decimal
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()


class FoodAnalysis(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    brand: str | None = Field(default=None, max_length=100)

    serving_size: Decimal = Field(gt=0)
    serving_unit: str

    calories: int = Field(ge=0)
    protein_g: Decimal = Field(ge=0)
    carbs_g: Decimal = Field(ge=0)
    fat_g: Decimal = Field(ge=0)
    fiber_g: Decimal | None = Field(default=None, ge=0)


async def analyze_food(
    image_bytes: bytes,
    mime_type: str,
    weight_category: str | None = None
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)

    prompt = """
    You are a food recognition and nutritional analysis system.

    Analyze the provided image and identify the food.

    Your response MUST match the FoodAnalysis schema exactly.

    FOOD IDENTIFICATION:
    - Identify the food shown in the image.
    - Use a concise, descriptive food name.
    - If a recognizable brand is visible, provide its name.
    - Otherwise, set brand to null.

    SERVING SIZE:
    - serving_size MUST ALWAYS be 100.
    - serving_unit MUST ALWAYS be "g".
    - All nutritional values MUST represent exactly 100 grams.
    - Ignore the actual portion size visible in the image.

    NUTRITIONAL VALUES:
    - calories: Estimated kilocalories per 100 grams.
    - protein_g: Estimated protein in grams per 100 grams.
    - carbs_g: Estimated carbohydrates in grams per 100 grams.
    - fat_g: Estimated fat in grams per 100 grams.
    - fiber_g: Estimated dietary fiber in grams per 100 grams.
    - If fiber cannot reasonably be estimated, return null.

    MULTIPLE FOODS:
    - If multiple foods are visible, identify the dish as a whole.
    - Estimate the proportion of each ingredient.
    - Calculate nutrition for 100 grams of the combined dish.
    - Do not return separate food objects.

    ACCURACY:
    - Use typical nutritional reference values.
    - Consider visible cooking methods and ingredients.
    - Do not invent a brand.
    - Never return negative nutritional values.
    - These values are estimates, not laboratory measurements.

    Return only valid JSON matching the provided schema.
    """

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FoodAnalysis
        )
    )

    if not response.text:
        raise RuntimeError("Gemini returned no analysis")

    data = json.loads(response.text)

    # Validate Gemini's response
    food = FoodAnalysis.model_validate(data)

    # Enforce exactly 100 grams, regardless of model output
    food.serving_size = Decimal("100")
    food.serving_unit = "g"

    # Convert Decimal fields to JSON-compatible values
    return food.model_dump(mode="json")

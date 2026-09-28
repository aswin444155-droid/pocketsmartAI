from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from google import genai
from dotenv import load_dotenv
import os, time, uuid
from datetime import datetime

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

try:
    from state import recommendation_history
except ImportError:
    from ..state import recommendation_history

load_dotenv()
router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_genai_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class HomeRequest(BaseModel):
    budget: float
    rooms: str
    style: Optional[str] = "Modern"
    room_types: Optional[List[str]] = []
    platforms: Optional[List[str]] = ["Amazon", "Flipkart", "IKEA"]
    preferences: Optional[str] = ""

def get_home_recommendations(budget, rooms, style, room_types, platforms, preferences):
    room_list     = ", ".join(room_types) if room_types else "Living Room, Bedroom"
    platform_list = ", ".join(platforms)  if platforms  else "Amazon, Flipkart, IKEA"

    prompt = f"""
You are an expert home interior designer and budget planner for India.

Generate a home interior budget plan for:
- Total Budget: Rs.{budget}
- Rooms: {rooms}
- Style: {style}
- Rooms to furnish: {room_list}
- Platforms: {platform_list}
- Preferences: {preferences or 'None'}

Return ONLY a valid JSON object in this exact format (no markdown, no explanation):
{{
  "categories": [
    {{
      "name": "Lighting",
      "icon": "💡",
      "allocation": 5000,
      "items": [
        {{
          "name": "LED Ceiling Light",
          "description": "Energy-efficient for living room",
          "price": 1200,
          "quantity": 3
        }}
      ]
    }},
    {{
      "name": "Furniture",
      "icon": "🛋️",
      "allocation": 20000,
      "items": [
        {{
          "name": "3-Seater Sofa",
          "description": "Comfortable fabric sofa in neutral tone",
          "price": 15000,
          "quantity": 1
        }}
      ]
    }}
  ],
  "tips": [
    "Buy during sale seasons like Big Billion Days on Flipkart for up to 70% off",
    "Consider second-hand furniture from OLX for heavy items",
    "Prioritize essential furniture first and add decor later"
  ]
}}

Rules:
- Create 3-5 categories relevant to the rooms selected
- Each category must have 2-4 items
- All prices must be realistic for India in 2024-26 in INR
- Total of all allocations must equal approximately Rs.{budget}
- Return ONLY the JSON, nothing else
"""
    client = get_genai_client()
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]
    last_err = None
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                if "404" in err_str or "not found" in err_str:
                    break
                if ("503" in err_str or "unavailable" in err_str) and attempt < 1:
                    time.sleep(2)
                    continue
                break
    raise last_err or Exception("Failed to generate home recommendations")

@router.get("/home-planner")
async def home_planner_page(request: Request):
    return templates.TemplateResponse(request=request, name="home_planner.html")

@router.post("/generate-home")
async def generate_home(data: HomeRequest):
    try:
        recommendations = get_home_recommendations(
            data.budget, data.rooms, data.style,
            data.room_types, data.platforms, data.preferences
        )
        recommendation_history.append({
            "id": str(uuid.uuid4()),
            "category": "home",
            "budget": data.budget,
            "preferences": {
                "rooms": data.rooms, "style": data.style,
                "room_types": data.room_types, "platforms": data.platforms
            },
            "result": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"recommendations": recommendations, "budget": data.budget}
    except Exception as e:
        return {"detail": f"AI generation failed: {str(e)}"}

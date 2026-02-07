from fastapi import APIRouter
from typing import Optional
from services import weather
from cores.utils import to_native_types

router = APIRouter()

@router.get("/travel-pack")
def travel_pack(city: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None):
    temp, rain, weather_details = weather.get_weather(city=city, lat=lat, lon=lon)

    clothes = {
        "tops": [],
        "bottoms": [],
        "outerwear": [],
        "footwear": [],
        "accessories": []
    }

    #  EXTREME COLD (≤ 5°C)
    if temp <= 5:
        clothes["tops"] = ["thermal top", "wool sweater"]
        clothes["bottoms"] = ["thermal pants", "thick trousers"]
        clothes["outerwear"] = ["heavy jacket", "puffer coat"]
        clothes["footwear"] = ["insulated boots"]
        clothes["accessories"] = ["gloves", "woolen cap", "scarf"]

    #  COLD (6–12°C)
    elif 6 <= temp <= 12:
        clothes["tops"] = ["full sleeve shirts", "wool sweaters"]
        clothes["bottoms"] = ["jeans", "warm trousers"]
        clothes["outerwear"] = ["jackets"]
        clothes["footwear"] = ["closed shoes"]
        clothes["accessories"] = ["light scarf"]

    #  COOL (13–18°C)
    elif 13 <= temp <= 18:
        clothes["tops"] = ["full sleeve t-shirts", "light sweaters"]
        clothes["bottoms"] = ["jeans", "chinos"]
        clothes["outerwear"] = ["light jacket", "hoodie"]
        clothes["footwear"] = ["sneakers"]
        clothes["accessories"] = ["watch"]

    #  MILD (19–24°C)
    elif 19 <= temp <= 24:
        clothes["tops"] = ["cotton shirts", "t-shirts"]
        clothes["bottoms"] = ["jeans", "skirts"]
        clothes["outerwear"] = ["light shrug"]
        clothes["footwear"] = ["sneakers", "sandals"]
        clothes["accessories"] = ["sunglasses"]

    #  WARM (25–30°C)
    elif 25 <= temp <= 30:
        clothes["tops"] = ["loose cotton t-shirts", "cotton shirts"]
        clothes["bottoms"] = ["jeans", "palazzo pants", "skirts"]
        clothes["outerwear"] = []
        clothes["footwear"] = ["sandals", "breathable shoes"]
        clothes["accessories"] = ["cap", "sunglasses"]

    #  HOT (31–36°C)
    elif 31 <= temp <= 36:
        clothes["tops"] = ["very light cotton tops", "sleeveless tops"]
        clothes["bottoms"] = ["shorts", "skirts", "loose pants"]
        clothes["outerwear"] = []
        clothes["footwear"] = ["sandals", "flip-flops"]
        clothes["accessories"] = ["cap", "sunglasses", "sunscreen"]

    #  EXTREME HOT (> 36°C)
    else:
        clothes["tops"] = ["ultra-light cotton tops"]
        clothes["bottoms"] = ["shorts"]
        clothes["outerwear"] = []
        clothes["footwear"] = ["open sandals"]
        clothes["accessories"] = ["cap", "sunglasses", "hydration bottle"]

    #  RAIN LOGIC
    if rain >= 10:
        clothes["outerwear"].append("raincoat")
        clothes["footwear"].append("waterproof shoes")
        clothes["accessories"].append("umbrella")

    return to_native_types({
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "temperature": round(float(temp), 1),
        "rain_probability": float(rain),
        "packing_recommendation": clothes
    })

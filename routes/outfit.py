from fastapi import APIRouter, UploadFile, File
from PIL import Image

from ml.extract_features import extract_features
from ml.classifier import predict_outfit_type
from services import weather as weather_svc
from services import material as material_svc
from services import alternatives as alt_svc
from services import accessories as acc_svc
from rules.outfit_weather import outfit_weather_check, combine_verdicts
from cores.utils import to_native_types, confidence_message

router = APIRouter()


@router.post("/predict-outfit")
async def predict_outfit(file: UploadFile = File(...)):
    image = Image.open(file.file)
    features = extract_features(image)

    outfit, confidence = predict_outfit_type(features)

    return to_native_types({"outfit_type": outfit, "confidence": confidence})


@router.post("/outfit-weather")
async def outfit_weather(file: UploadFile = File(...), city: str = "Delhi", material: str = "cotton", occasion: str = None):
    image = Image.open(file.file)
    features = extract_features(image)

    outfit, confidence = predict_outfit_type(features)
    temp, rain, weather_details = weather_svc.get_weather(city)

    outfit_verdict = outfit_weather_check(outfit, temp, rain)
    accessories = acc_svc.get_all_accessories(outfit, temp, rain, occasion)

    material_feedback = material_svc.material_analysis(material, temp)
    final_verdict = combine_verdicts(outfit_verdict, material_feedback.get("verdict"))

    alternatives = alt_svc.get_better_alternatives(outfit, temp)

    response = {
        "outfit_type": outfit,
        "material": material,
        "confidence": confidence,
        "confidence_message": confidence_message(confidence),
        "temperature": float(temp),
        "rain_probability": float(rain),
        "rain_advice": acc_svc.rain_accessories(rain),
        "weather_breakdown": weather_details,
        "outfit_verdict": outfit_verdict,
        "material_verdict": material_feedback.get("verdict"),
        "material_reason": material_feedback.get("reason"),
        "final_verdict": final_verdict,
        "suggested_alternatives": alternatives,
        "accessories": accessories,
    }

    return to_native_types(response)

from fastapi import APIRouter, UploadFile, File, Body
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import os
import json
from datetime import datetime

from ml.extract_features import extract_features
from ml.classifier import predict_outfit_type, get_available_categories
from services import weather as weather_svc
from services import material as material_svc
from services import alternatives as alt_svc
from services import accessories as acc_svc
from rules.outfit_weather import outfit_weather_check, combine_verdicts
from cores.utils import to_native_types, confidence_message

router = APIRouter()

# Confidence threshold - if below this, ask user to confirm
CONFIDENCE_THRESHOLD = 0.6


@router.post("/predict-outfit")
async def predict_outfit(file: UploadFile = File(...)):
    """
    Predict outfit type from image.
    Returns prediction with confidence and needs_confirmation flag.
    """
    image = Image.open(file.file)
    features = extract_features(image)

    outfit, confidence = predict_outfit_type(features)
    
    needs_confirmation = confidence < CONFIDENCE_THRESHOLD

    return to_native_types({
        "predicted_class": outfit,
        "confidence": confidence,
        "needs_confirmation": needs_confirmation,
        "confidence_message": confidence_message(confidence)
    })


@router.get("/outfit-categories")
async def get_outfit_categories():
    """
    Get all available outfit categories for manual selection.
    """
    categories = get_available_categories()
    return {"categories": categories}


@router.post("/outfit-weather")
async def outfit_weather(
    file: UploadFile = File(...), 
    city: str = "Delhi", 
    material: str = "cotton", 
    occasion: Optional[str] = None,
    manual_outfit_type: Optional[str] = None
):
    """
    Get outfit weather recommendations.
    If manual_outfit_type is provided, use it instead of ML prediction.
    """
    image = Image.open(file.file)
    features = extract_features(image)

    # Use manual selection if provided, otherwise use ML prediction
    if manual_outfit_type:
        outfit = manual_outfit_type.lower()
        confidence = 1.0  # User-selected, so 100% confidence
    else:
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


# Feedback model for user corrections
class FeedbackRequest(BaseModel):
    image_url: Optional[str] = None
    user_selected_category: str
    model_predicted_category: Optional[str] = None
    confidence: Optional[float] = None
    notes: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback/correction for model improvement.
    This data can be used later for retraining the model.
    """
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "user_selected_category": feedback.user_selected_category,
        "model_predicted_category": feedback.model_predicted_category,
        "confidence": feedback.confidence,
        "image_url": feedback.image_url,
        "notes": feedback.notes
    }
    
    # Save feedback to a file (you can later use this for retraining)
    feedback_dir = "feedback_data"
    os.makedirs(feedback_dir, exist_ok=True)
    
    feedback_file = os.path.join(feedback_dir, f"feedback_{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    try:
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_data) + "\n")
        
        return {
            "message": "Feedback saved successfully",
            "status": "success"
        }
    except Exception as e:
        return {
            "message": f"Error saving feedback: {str(e)}",
            "status": "error"
        }

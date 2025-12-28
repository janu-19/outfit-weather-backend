from fastapi import APIRouter, UploadFile, File, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserUpload
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


from cloudinary_config import upload_image_to_cloudinary
import io

@router.post("/predict-outfit")
async def predict_outfit(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Predict outfit type from image.
    Uploads image to Cloudinary and returns prediction with confidence.
    """
    # 1. Read bytes
    image_bytes = await file.read()
    
    # 2. Upload to Cloudinary
    try:
        upload_result = upload_image_to_cloudinary(image_bytes, folder="outfit_predictions")
        image_url = upload_result["secure_url"]
        public_id = upload_result["public_id"]
    except Exception as e:
        # If upload fails, we log/print but might still want to return prediction? 
        # Or fail? The user specifically wants uploads. So let's handle it safely but try to proceed or report error?
        # Let's report error if upload is critical, or just print it. 
        # Given user request "i checked... not uploading", they treat it as a bug.
        print(f"Warning: Cloudinary upload failed: {e}")
        image_url = None
        public_id = None

    # 3. Predict
    image = Image.open(io.BytesIO(image_bytes))
    features = extract_features(image)

    outfit, confidence = predict_outfit_type(features)
    
    needs_confirmation = confidence < CONFIDENCE_THRESHOLD


    user_upload = UserUpload(
        image_url=image_url if image_url else "",
        public_id=public_id,
        predicted_category=outfit,
        confidence=confidence,
        is_verified=0
    )
    db.add(user_upload)
    db.commit()
    db.refresh(user_upload)

    return to_native_types({
        "id": user_upload.id,
        "predicted_class": outfit,
        "confidence": confidence,
        "image_url": image_url,
        "public_id": public_id,
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
class VerifyRequest(BaseModel):
    image_id: int
    user_label: str


@router.post("/verify-outfit")
async def verify_outfit(verify_data: VerifyRequest, db: Session = Depends(get_db)):
    """
    Verify/Correct a prediction.
    Updates the database with the correct label and marks as verified.
    """
    upload = db.query(UserUpload).filter(UserUpload.id == verify_data.image_id).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Image record not found")
    
    upload.user_label = verify_data.user_label
    upload.is_verified = 1
    db.commit()
    
    return {
        "message": "Verification saved successfully", 
        "status": "success",
        "verified_label": verify_data.user_label
    }

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


from auth import get_current_user
from models import User, Prediction, Feedback

@router.post("/predict/guest")
async def predict_guest(
    file: UploadFile = File(...), 
    city: str = "Delhi",
    match_weather: bool = True
):
    """
    Guest Mode:
    - In-memory processing only.
    - No Cloudinary upload.
    - No database storage.
    - Returns prediction and weather advice.
    """
    # 1. Read bytes
    image_bytes = await file.read()
    
    # 2. Predict (In-memory)
    image = Image.open(io.BytesIO(image_bytes))
    features = extract_features(image)
    outfit, confidence = predict_outfit_type(features)
    
    response = {
        "predicted_class": outfit,
        "confidence": confidence,
        "confidence_message": confidence_message(confidence),
        "is_guest": True
    }

    # 3. Weather check (Optional)
    if match_weather:
        temp, rain_vol, details = weather_svc.get_weather(city)
        # Use new rules signature
        outfit_verdict = outfit_weather_check(
            outfit, 
            temp, 
            rain_vol, 
            min_temp=details.get("min_temp"), 
            max_temp=details.get("max_temp"), 
            rain_prob=details.get("daily_rain_prob")
        )
        
        response.update({
            "weather": {
                "city": city,
                "temperature": temp,
                "rain_prob": details.get("daily_rain_prob"),
                "description": details.get("description"),
                "verdict": outfit_verdict
            }
        })

    return to_native_types(response)


@router.post("/predict/auth")
async def predict_auth(
    file: UploadFile = File(...), 
    city: str = "Delhi", 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authenticated Mode:
    - Uploads to Cloudinary.
    - Saves to 'predictions' table.
    - Returns prediction_id for potential feedback/wardrobe saving.
    """
    # 1. Read bytes
    image_bytes = await file.read()
    
    # 2. Upload to Cloudinary
    try:
        upload_result = upload_image_to_cloudinary(image_bytes, folder="outfit_predictions")
        image_url = upload_result["secure_url"]
        public_id = upload_result["public_id"]
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed")

    # 3. Predict
    image = Image.open(io.BytesIO(image_bytes))
    features = extract_features(image)
    outfit, confidence = predict_outfit_type(features)
    
    # 4. Get Weather
    temp, rain_vol, details = weather_svc.get_weather(city)
    
    # 5. Save Prediction
    weather_snapshot = json.dumps({
        "city": city,
        "temp": temp,
        "description": details.get("description"),
        "min": details.get("min_temp"),
        "max": details.get("max_temp")
    })
    
    new_prediction = Prediction(
        user_id=current_user.id,
        image_url=image_url,
        public_id=public_id,
        predicted_category=outfit,
        confidence=confidence,
        weather_data=weather_snapshot
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    # 6. Run Rules (for response only)
    outfit_verdict = outfit_weather_check(
        outfit, 
        temp, 
        rain_vol, 
        min_temp=details.get("min_temp"), 
        max_temp=details.get("max_temp"), 
        rain_prob=details.get("daily_rain_prob")
    )
    
    # 7. Alternatives & Accessories
    accessories = acc_svc.get_all_accessories(outfit, temp, rain_vol)
    
    return to_native_types({
        "prediction_id": new_prediction.id,
        "predicted_class": outfit,
        "confidence": confidence,
        "image_url": image_url,
        "weather_verdict": outfit_verdict,
        "accessories": accessories,
        "weather_summary": details
    })



class FeedbackRequest(BaseModel):
    prediction_id: Optional[int] = None
    user_label: Optional[str] = None
    is_helpful: bool = True
    weather_context: Optional[dict] = None # For guest feedback
    model_output: Optional[dict] = None    # For guest feedback


@router.post("/feedback")
async def submit_feedback(
    feedback_data: FeedbackRequest, 
    current_user: Optional[User] = Depends(get_current_user), # Optional Auth
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a prediction.
    - specific prediction_id (Auth users)
    - OR generic context (Guest users, logic-only feedback)
    """
    
    # Validation: Need either ID or Context
    if not feedback_data.prediction_id and not (feedback_data.weather_context and feedback_data.model_output):
        raise HTTPException(status_code=400, detail="Must provide prediction_id (Auth) or context (Guest)")

    # If linked to prediction, verify ownership
    if feedback_data.prediction_id:
        prediction = db.query(Prediction).filter(Prediction.id == feedback_data.prediction_id).first()
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # If user is authenticated, check ownership
        # If prediction has user_id, current_user must match
        if prediction.user_id and (not current_user or current_user.id != prediction.user_id):
             raise HTTPException(status_code=403, detail="Not authorized to provide feedback for this prediction")

    # Serialize context if provided
    weather_json = json.dumps(feedback_data.weather_context) if feedback_data.weather_context else None
    output_json = json.dumps(feedback_data.model_output) if feedback_data.model_output else None

    new_feedback = Feedback(
        prediction_id=feedback_data.prediction_id,
        user_id=current_user.id if current_user else None,
        user_label=feedback_data.user_label,
        is_helpful=1 if feedback_data.is_helpful else 0,
        weather_context=weather_json,
        model_output=output_json
    )
    
    db.add(new_feedback)
    db.commit()
    
    return {"status": "success", "message": "Feedback received"}


@router.get("/debug/verified-uploads")
async def get_verified_uploads(db: Session = Depends(get_db)):
    """
    Debug: View qualitative feedback.
    """
    feedbacks = db.query(Feedback).all()
    results = []
    
    for f in feedbacks:
        item = {
            "id": f.id,
            "user_label": f.user_label,
            "is_helpful": bool(f.is_helpful),
            "created_at": f.created_at
        }
        
        if f.prediction:
            item["image_url"] = f.prediction.image_url
            item["predicted"] = f.prediction.predicted_category
        else:
            item["context"] = "Guest Feedback (No Image)"
            
        results.append(item)
            
    return results

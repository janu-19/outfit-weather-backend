"""
Wardrobe management routes
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta
from pydantic import BaseModel

from database import get_db, init_db
from models import Outfit
from cloudinary_config import upload_image_to_cloudinary
from ml.extract_features import extract_features
from ml.classifier import predict_outfit_type
from PIL import Image
import io

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])

# Initialize database on first import
init_db()


class OutfitCreate(BaseModel):
    image_url: str
    category: str
    color: Optional[str] = None
    occasion: Optional[str] = None
    notes: Optional[str] = None
    confidence: Optional[float] = None


class OutfitUpdate(BaseModel):
    category: Optional[str] = None
    color: Optional[str] = None
    occasion: Optional[str] = None
    notes: Optional[str] = None


@router.post("/upload-outfit")
async def upload_outfit(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload outfit image to Cloudinary and optionally run ML prediction.
    Returns image URL and prediction.
    """
    # Read image bytes
    image_bytes = await file.read()
    
    # Upload to Cloudinary
    try:
        upload_result = upload_image_to_cloudinary(image_bytes)
        image_url = upload_result["secure_url"]
        public_id = upload_result["public_id"]
    except ValueError as e:
        # Credential validation error
        raise HTTPException(
            status_code=400, 
            detail=f"Cloudinary configuration error: {str(e)}. Please check your .env file."
        )
    except Exception as e:
        error_msg = str(e)
        if "Invalid Signature" in error_msg or "signature" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Cloudinary authentication failed. Please verify your CLOUDINARY_API_SECRET in .env file. Make sure there are no extra spaces or quotes."
            )
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
    # Optional: Run ML prediction
    try:
        image = Image.open(io.BytesIO(image_bytes))
        features = extract_features(image)
        category, confidence = predict_outfit_type(features)
    except Exception as e:
        # If prediction fails, still return image URL
        category = "unknown"
        confidence = 0.0
    
    return {
        "image_url": image_url,
        "public_id": public_id,
        "predicted_category": category,
        "confidence": confidence,
        "message": "Image uploaded successfully"
    }


@router.post("/save-outfit")
async def save_outfit(
    outfit_data: OutfitCreate,
    db: Session = Depends(get_db)
):
    """
    Save outfit to wardrobe database.
    """
    outfit = Outfit(
        image_url=outfit_data.image_url,
        category=outfit_data.category,
        color=outfit_data.color,
        occasion=outfit_data.occasion,
        notes=outfit_data.notes,
        confidence=outfit_data.confidence
    )
    
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    
    return {
        "message": "Outfit saved successfully",
        "outfit": outfit.to_dict()
    }


@router.get("/outfits")
async def get_wardrobe(
    category: Optional[str] = None,
    occasion: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all outfits from wardrobe with optional filters.
    """
    query = db.query(Outfit)
    
    if category:
        query = query.filter(Outfit.category == category.lower())
    if occasion:
        query = query.filter(Outfit.occasion == occasion.lower())
    
    outfits = query.order_by(Outfit.created_at.desc()).all()
    
    return {
        "count": len(outfits),
        "outfits": [outfit.to_dict() for outfit in outfits]
    }


@router.get("/outfit/{outfit_id}")
async def get_outfit(
    outfit_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific outfit by ID.
    """
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    return outfit.to_dict()


@router.put("/outfit/{outfit_id}")
async def update_outfit(
    outfit_id: int,
    outfit_update: OutfitUpdate,
    db: Session = Depends(get_db)
):
    """
    Update outfit details.
    """
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    if outfit_update.category:
        outfit.category = outfit_update.category
    if outfit_update.color:
        outfit.color = outfit_update.color
    if outfit_update.occasion:
        outfit.occasion = outfit_update.occasion
    if outfit_update.notes is not None:
        outfit.notes = outfit_update.notes
    
    db.commit()
    db.refresh(outfit)
    
    return {
        "message": "Outfit updated successfully",
        "outfit": outfit.to_dict()
    }


@router.delete("/outfit/{outfit_id}")
async def delete_outfit(
    outfit_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete outfit from wardrobe.
    """
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    db.delete(outfit)
    db.commit()
    
    return {"message": "Outfit deleted successfully"}


@router.post("/wear-outfit/{outfit_id}")
async def wear_outfit(
    outfit_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark outfit as worn today.
    """
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    outfit.last_worn_date = date.today()
    db.commit()
    db.refresh(outfit)
    
    return {
        "message": "Outfit marked as worn",
        "outfit": outfit.to_dict()
    }


@router.get("/outfits-by-date/{wear_date}")
async def outfits_by_date(
    wear_date: str,
    db: Session = Depends(get_db)
):
    """
    Get all outfits worn on a specific date.
    Date format: YYYY-MM-DD
    """
    try:
        target_date = date.fromisoformat(wear_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    outfits = db.query(Outfit).filter(
        Outfit.last_worn_date == target_date
    ).all()
    
    return {
        "date": wear_date,
        "count": len(outfits),
        "outfits": [outfit.to_dict() for outfit in outfits]
    }


@router.get("/not-worn-recently")
async def not_worn_recently(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get outfits not worn in the last N days.
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    outfits = db.query(Outfit).filter(
        (Outfit.last_worn_date < cutoff_date) | (Outfit.last_worn_date.is_(None))
    ).all()
    
    return {
        "days": days,
        "cutoff_date": cutoff_date.isoformat(),
        "count": len(outfits),
        "outfits": [outfit.to_dict() for outfit in outfits]
    }


@router.get("/suggest-outfits")
async def suggest_outfits(
    category: Optional[str] = None,
    occasion: Optional[str] = None,
    avoid_recent: bool = True,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Smart outfit suggestions based on:
    - Category (optional)
    - Occasion (optional)
    - Avoid recently worn outfits
    """
    query = db.query(Outfit)
    
    # Filter by category if provided
    if category:
        query = query.filter(Outfit.category == category.lower())
    
    # Filter by occasion if provided
    if occasion:
        query = query.filter(Outfit.occasion == occasion.lower())
    
    # Avoid recently worn outfits
    if avoid_recent:
        cutoff_date = date.today() - timedelta(days=days)
        query = query.filter(
            (Outfit.last_worn_date < cutoff_date) | (Outfit.last_worn_date.is_(None))
        )
    
    # Order by least recently worn (or never worn)
    outfits = query.order_by(Outfit.last_worn_date.asc().nullsfirst()).limit(10).all()
    
    return {
        "count": len(outfits),
        "outfits": [outfit.to_dict() for outfit in outfits]
    }


@router.get("/stats")
async def wardrobe_stats(db: Session = Depends(get_db)):
    """
    Get wardrobe statistics.
    """
    total_outfits = db.query(Outfit).count()
    
    # Count by category
    categories = db.query(Outfit.category).distinct().all()
    category_counts = {}
    for cat in categories:
        count = db.query(Outfit).filter(Outfit.category == cat[0]).count()
        category_counts[cat[0]] = count
    
    # Count never worn
    never_worn = db.query(Outfit).filter(Outfit.last_worn_date.is_(None)).count()
    
    # Count worn in last 7 days
    week_ago = date.today() - timedelta(days=7)
    recently_worn = db.query(Outfit).filter(Outfit.last_worn_date >= week_ago).count()
    
    return {
        "total_outfits": total_outfits,
        "categories": category_counts,
        "never_worn": never_worn,
        "recently_worn_7_days": recently_worn
    }


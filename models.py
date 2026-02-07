"""
Database models for wardrobe system
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    outfits = relationship("Outfit", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="owner", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    public_id = Column(String, nullable=True)  # Cloudinary public_id
    category = Column(String, nullable=False)  # e.g., "dress", "shirt", "jeans"
    color = Column(String, nullable=True)
    occasion = Column(String, nullable=True)  # e.g., "casual", "formal", "party"
    last_worn_date = Column(Date, nullable=True)
    confidence = Column(Float, nullable=True)  # ML prediction confidence
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key to User
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="outfits")

    def to_dict(self):
        """Convert outfit to dictionary"""
        return {
            "id": self.id,
            "image_url": self.image_url,
            "public_id": self.public_id,
            "category": self.category,
            "color": self.color,
            "occasion": self.occasion,
            "last_worn_date": self.last_worn_date.isoformat() if self.last_worn_date else None,
            "confidence": self.confidence,
            "notes": self.notes,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Prediction(Base):
    """
    Store predictions for AUTHENTICATED users.
    Guest predictions are not stored.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    # Allow null for guest predictions
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_guest = Column(Boolean, default=False, nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True) # If saved to wardrobe
    
    # For guest predictions we do not store images
    image_url = Column(String, nullable=True)
    public_id = Column(String, nullable=True)
    
    predicted_category = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    weather_data = Column(String, nullable=True) # JSON string (min/max/rain prob)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="predictions")
    feedback = relationship("Feedback", back_populates="prediction", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "predicted_category": self.predicted_category,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Feedback(Base):
    """
    Store user feedback for predictions.
    Can be linked to a Prediction (auth) or standalone (guest context).
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Null for guests
    
    weather_context = Column(String, nullable=True) # JSON string
    model_output = Column(String, nullable=True) # JSON string
    user_label = Column(String, nullable=True) # Manual correction
    is_helpful = Column(Integer, default=1) # 1=Yes, 0=No
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    prediction = relationship("Prediction", back_populates="feedback")


class UserUpload(Base):
    """
    DEPRECATED: Replaced by Prediction and Feedback tables.
    Kept for backward compatibility to avoid migration errors if table exists.
    """
    __tablename__ = "user_uploads"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    public_id = Column(String, nullable=True) 
    predicted_category = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    user_label = Column(String, nullable=True) 
    is_verified = Column(Integer, default=0)   
    created_at = Column(DateTime(timezone=True), server_default=func.now())


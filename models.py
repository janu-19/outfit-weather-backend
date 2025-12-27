"""
Database models for wardrobe system
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey
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


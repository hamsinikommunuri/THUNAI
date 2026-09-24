"""
THUNAI SQLAlchemy Database Models
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from backend.app.db.database import Base

class DiagnosisRecord(Base):
    __tablename__ = "diagnoses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop = Column(String(50), nullable=False)
    disease_id = Column(String(100), nullable=False)
    disease_name = Column(String(150), nullable=False)
    scientific_name = Column(String(150), nullable=True)
    confidence = Column(Float, nullable=False)
    confidence_tier = Column(String(20), nullable=False) # High, Moderate, Low
    top_predictions = Column(JSON, nullable=True)
    
    # Image Paths / Base64
    image_url = Column(Text, nullable=True)
    gradcam_url = Column(Text, nullable=True)
    
    # Environmental Snapshots
    location_district = Column(String(100), nullable=True)
    location_state = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    weather_snapshot = Column(JSON, nullable=True)
    soil_snapshot = Column(JSON, nullable=True)
    
    # Spray & Treatment Decisions
    spray_recommendation = Column(String(50), nullable=True) # SPRAY NOW, WAIT, NOT RECOMMENDED
    spray_reason = Column(Text, nullable=True)
    treatment_recommended = Column(JSON, nullable=True)
    dose_locked = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ExpertEscalation(Base):
    __tablename__ = "expert_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dossier_id = Column(String(50), unique=True, nullable=False)
    diagnosis_id = Column(String(36), nullable=True)
    crop = Column(String(50), nullable=False)
    district = Column(String(100), nullable=True)
    farmer_phone = Column(String(20), nullable=True)
    escalation_reason = Column(Text, nullable=False)
    status = Column(String(50), default="DISPATCH_READY") # DISPATCH_READY, IN_REVIEW, RESOLVED
    dossier_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

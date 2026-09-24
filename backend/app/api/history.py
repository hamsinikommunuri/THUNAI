"""
THUNAI Diagnosis History API Endpoint
Allows farmers to retrieve and review previous diagnosis records.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.db.database import get_db
from backend.app.db.models import DiagnosisRecord
from backend.app.schemas.schemas import HistoryItemResponse

router = APIRouter(prefix="/history", tags=["Diagnosis History"])

@router.get("", response_model=List[HistoryItemResponse])
async def list_recent_diagnoses(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(DiagnosisRecord).order_by(desc(DiagnosisRecord.created_at)).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()

    items = []
    for r in records:
        items.append(HistoryItemResponse(
            id=r.id,
            crop=r.crop,
            disease_name=r.disease_name,
            scientific_name=r.scientific_name,
            confidence=r.confidence,
            confidence_tier=r.confidence_tier,
            image_url=r.image_url,
            location_district=r.location_district,
            spray_recommendation=r.spray_recommendation,
            created_at=r.created_at.strftime("%Y-%m-%d %H:%M UTC") if r.created_at else "Recently"
        ))
    return items

@router.get("/{id}")
async def get_diagnosis_detail(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    query = select(DiagnosisRecord).where(DiagnosisRecord.id == id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Diagnosis record not found.")

    return {
        "id": record.id,
        "crop": record.crop,
        "disease_name": record.disease_name,
        "scientific_name": record.scientific_name,
        "confidence": record.confidence,
        "confidence_tier": record.confidence_tier,
        "top_predictions": record.top_predictions,
        "image_url": record.image_url,
        "location_district": record.location_district,
        "location_state": record.location_state,
        "weather_snapshot": record.weather_snapshot,
        "spray_recommendation": record.spray_recommendation,
        "spray_reason": record.spray_reason,
        "treatment_recommended": record.treatment_recommended,
        "created_at": record.created_at.strftime("%Y-%m-%d %H:%M UTC") if record.created_at else "Recently"
    }

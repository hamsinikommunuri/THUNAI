"""
THUNAI Expert Escalation API Endpoint
Generates traceable Agronomist Case Dossiers and maps district KVK centers.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.database import get_db
from backend.app.db.models import ExpertEscalation
from backend.app.schemas.schemas import ExpertEscalationRequest, ExpertEscalationResponse
from backend.app.services.expert_service import ExpertEscalationService

router = APIRouter(prefix="/expert", tags=["Expert Escalation & Second Opinion"])

@router.post("/escalation", response_model=ExpertEscalationResponse)
async def request_second_opinion(
    payload: ExpertEscalationRequest,
    db: AsyncSession = Depends(get_db)
):
    dossier = ExpertEscalationService.create_case_dossier(
        crop=payload.crop,
        district=payload.district,
        diagnosis_id=payload.diagnosis_id,
        reason=payload.reason,
        farmer_phone=payload.farmer_phone
    )

    # Persist to database
    record = ExpertEscalation(
        dossier_id=dossier["dossier_id"],
        diagnosis_id=payload.diagnosis_id,
        crop=payload.crop,
        district=payload.district,
        farmer_phone=payload.farmer_phone,
        escalation_reason=payload.reason,
        status="DISPATCH_READY",
        dossier_data=dossier["downloadable_dossier_summary"]
    )
    db.add(record)
    await db.commit()

    return ExpertEscalationResponse(
        dossier_id=dossier["dossier_id"],
        status="DISPATCH_READY",
        crop=dossier["crop"],
        district=dossier["district"],
        timestamp=dossier["timestamp"],
        kvk_center=dossier["kvk_center"],
        helpline=dossier["helpline"],
        downloadable_dossier_summary=dossier["downloadable_dossier_summary"],
        dispatch_message=dossier["dispatch_message"]
    )

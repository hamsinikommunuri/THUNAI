"""FastAPI Backend Server for THUNAI Field Intelligence Web UI."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from thunai.core.enums import DecisionType, ReasonCode
from thunai.core.models import FarmerContext
from thunai.knowledge.document_ingestion import DocumentIngestionEngine
from thunai.knowledge.retriever import HybridEvidenceRetriever
from thunai.knowledge.synonyms import AgriculturalSynonymNormalizer
from thunai.safety.dose_lock import DoseLockEngine
from thunai.safety.escalation import build_action_decision

app = FastAPI(
    title="THUNAI — Field Intelligence Backend",
    description="Deterministic agricultural safety, hybrid evidence retrieval, and decision support API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
corpus_engine = DocumentIngestionEngine()
retriever = HybridEvidenceRetriever(corpus_engine=corpus_engine)
safety_engine = DoseLockEngine()
normalizer = AgriculturalSynonymNormalizer()

ROOT_DIR = Path(__file__).resolve().parent.parent


class QueryRequest(BaseModel):
    query: str
    crop: Optional[str] = None
    language: str = "ta"
    growth_stage: Optional[str] = None
    days_to_harvest: Optional[int] = None
    requested_chemical: Optional[str] = None


class CropInfo(BaseModel):
    crop_id: str
    name_en: str
    name_ta: str
    scientific_name: str
    icon: str


@app.get("/debug")
@app.get("/api/debug")
def get_debug_info():
    return {"status": "ok", "service": "THUNAI"}


@app.get("/crops", response_model=List[CropInfo])
@app.get("/api/crops", response_model=List[CropInfo])
def get_supported_crops():
    """Returns the 4 controlled Phase 1 crops."""
    return [
        CropInfo(
            crop_id="paddy",
            name_en="Paddy / Rice",
            name_ta="நெல்",
            scientific_name="Oryza sativa",
            icon="🌾",
        ),
        CropInfo(
            crop_id="tomato",
            name_en="Tomato",
            name_ta="தக்காளி",
            scientific_name="Solanum lycopersicum",
            icon="🍅",
        ),
        CropInfo(
            crop_id="banana",
            name_en="Banana",
            name_ta="வாழை",
            scientific_name="Musa paradisiaca",
            icon="🍌",
        ),
        CropInfo(
            crop_id="chilli",
            name_en="Chilli",
            name_ta="மிளகாய்",
            scientific_name="Capsicum annuum",
            icon="🌶️",
        ),
    ]


@app.post("/query")
@app.post("/api/query")
def process_farmer_query(req: QueryRequest) -> Dict[str, Any]:
    """Processes farmer query through Context Isolation -> Hybrid Retrieval -> DoseLock -> Advisory."""
    # 1. Build FarmerContext
    context = FarmerContext(
        raw_query=req.query,
        crop=req.crop,
        language=req.language,
        growth_stage=req.growth_stage,
        days_to_harvest=req.days_to_harvest,
        requested_chemical=req.requested_chemical,
    )

    # 2. Hybrid Retrieval with hard crop isolation
    retrieval_res = retriever.retrieve(req.query, context=context, top_k=3)

    # 3. Candidate records
    top_candidate = retrieval_res.candidates[0] if retrieval_res.candidates else None
    if top_candidate and not context.target_problem:
        context.target_problem = top_candidate.problem
        context.problem_id = top_candidate.problem_id

    # 4. Evaluate Safety Decision
    safety_decision = safety_engine.evaluate(context=context, evidence=top_candidate)

    # 5. Build Action Decision
    action_decision = build_action_decision(safety_decision=safety_decision, context=context)

    # 6. Format candidate details
    candidate_details = []
    for idx, c in enumerate(retrieval_res.candidates):
        score = retrieval_res.scores[idx] if idx < len(retrieval_res.scores) else 0.0
        candidate_details.append({
            "evidence_id": c.evidence_id,
            "crop": c.crop,
            "crop_id": c.crop_id,
            "problem": c.problem,
            "problem_id": c.problem_id,
            "active_ingredient": c.active_ingredient,
            "formulation": c.formulation,
            "dose": c.dose,
            "dose_unit": c.dose_unit,
            "waiting_period_days": c.waiting_period_days,
            "source": c.source,
            "source_reference": c.source_reference,
            "notes": c.notes,
            "score": round(score, 3),
        })

    return {
        "query": req.query,
        "isolated_crop": context.crop or retrieval_res.filtered_crop_id,
        "isolated_crop_id": context.crop_id or retrieval_res.filtered_crop_id,
        "target_problem": context.target_problem,
        "problem_id": context.problem_id,
        "has_evidence": retrieval_res.has_evidence,
        "has_conflict": retrieval_res.has_conflict,
        "conflict_notes": retrieval_res.conflict_notes,
        "candidates": candidate_details,
        "safety_decision": {
            "decision": safety_decision.decision.value,
            "reason_code": safety_decision.reason_code.value,
            "human_reason": safety_decision.human_reason,
            "human_reason_ta": safety_decision.human_reason_ta,
            "is_allowed": safety_decision.is_allowed,
            "is_blocked": safety_decision.is_blocked,
            "is_escalated": safety_decision.is_escalated,
            "allowed_dose": safety_decision.allowed_dose.model_dump() if safety_decision.allowed_dose else None,
            "trace": safety_decision.trace,
        },
        "action_decision": {
            "status": action_decision.status.value,
            "can_recommend_chemical": action_decision.can_recommend_chemical,
            "can_recommend_dose": action_decision.can_recommend_dose,
            "recommended_action": action_decision.recommended_action,
            "farmer_message": action_decision.farmer_message,
            "farmer_message_ta": action_decision.farmer_message_ta,
            "escalation_needed": action_decision.escalation_needed,
            "escalation_reason": action_decision.escalation_reason,
            "next_step": action_decision.next_step,
        },
    }


@app.get("/")
def serve_ui():
    """Serves the interactive THUNAI UI."""
    index_path = ROOT_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    html_path = ROOT_DIR / "code.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return HTMLResponse("<h1>THUNAI UI Not Found</h1>", status_code=404)


@app.get("/screen.png")
def serve_screenshot():
    """Serves the reference UI screenshot."""
    png_path = ROOT_DIR / "screen.png"
    if png_path.exists():
        return FileResponse(str(png_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Screenshot not found")


@app.get("/DESIGN.md")
def serve_design_system():
    """Serves the design specification."""
    md_path = ROOT_DIR / "DESIGN.md"
    if md_path.exists():
        return FileResponse(str(md_path), media_type="text/markdown")
    raise HTTPException(status_code=404, detail="DESIGN.md not found")
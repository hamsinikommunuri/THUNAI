"""
THUNAI Agricultural Decision Support Platform
FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.db.database import init_db
from backend.app.api.location import router as location_router
from backend.app.api.weather import router as weather_router
from backend.app.api.soil import router as soil_router
from backend.app.api.crops import router as crops_router
from backend.app.api.diagnosis import router as diagnosis_router
from backend.app.api.doselock import router as doselock_router
from backend.app.api.expert import router as expert_router
from backend.app.api.history import router as history_router
from ml.inference import get_inference_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database tables and load ML inference model once into memory
    print("Initializing THUNAI Platform Services...")
    await init_db()
    try:
        get_inference_engine()
        print("ML Inference Engine pre-warmed successfully.")
    except Exception as e:
        print(f"Notice: ML Engine lazy-init on first request ({e})")
    yield
    print("Shutting down THUNAI Platform Services.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="End-to-End Agricultural AI Web Application: Vision Diagnosis, Weather Shift, Dose Lock, and Soil Intelligence.",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local Vite, Next.js, and deployed frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads (if present)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Modular API Routers
app.include_router(location_router, prefix=settings.API_PREFIX)
app.include_router(weather_router, prefix=settings.API_PREFIX)
app.include_router(soil_router, prefix=settings.API_PREFIX)
app.include_router(crops_router, prefix=settings.API_PREFIX)
app.include_router(diagnosis_router, prefix=settings.API_PREFIX)
app.include_router(doselock_router, prefix=settings.API_PREFIX)
app.include_router(expert_router, prefix=settings.API_PREFIX)
app.include_router(history_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["System Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "THUNAI Agricultural Intelligence Platform",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "features": {
            "crop_vision_ml": True,
            "weather_intelligence": True,
            "spray_safety_engine": True,
            "soil_intelligence": True,
            "dose_lock_safety": True,
            "evidence_trace": True,
            "expert_escalation": True
        }
    }

# Serve static frontend SPA if built
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": "Welcome to THUNAI Agricultural AI Platform API",
            "docs_url": "/docs",
            "health_check": "/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

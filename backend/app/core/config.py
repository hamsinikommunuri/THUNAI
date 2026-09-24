"""
THUNAI Core Application Configuration
"""

import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "THUNAI Agricultural Intelligence Platform"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", 8000))
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./thunai.db")
    
    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ML_CHECKPOINT_PATH: str = os.path.join(BASE_DIR, "ml", "checkpoints", "best_model.pth")
    ML_ARTIFACTS_DIR: str = os.path.join(BASE_DIR, "ml", "artifacts")
    KNOWLEDGE_DIR: str = os.path.join(os.path.dirname(__file__), "..", "knowledge")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "backend", "uploads")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

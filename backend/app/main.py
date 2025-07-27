from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api import auth, upload, processing, dashboard
from app.api import enhanced_upload, enhanced_processing, rule_engine
from app.core.config import settings
from app.core.auth import verify_firebase_token
from app.core.database import init_db

load_dotenv()

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    pass

app = FastAPI(
    title="HSBC Enterprise Dashboard API",
    description="Enterprise-grade data processing and visualization platform for HSBC",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(token: str = Depends(security)):
    try:
        user = await verify_firebase_token(token.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["File Upload"])
app.include_router(enhanced_upload.router, prefix="/api/enhanced-upload", tags=["Enhanced Upload"])
app.include_router(processing.router, prefix="/api/processing", tags=["Data Processing"])
app.include_router(enhanced_processing.router, prefix="/api/enhanced-processing", tags=["Enhanced Processing"])
app.include_router(rule_engine.router, prefix="/api/rule-engine", tags=["Rule Engine"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {
        "message": "HSBC Enterprise Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
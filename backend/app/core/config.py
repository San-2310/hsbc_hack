from pydantic import Extra
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HSBC Enterprise Dashboard"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://hsbc-dashboard.vercel.app",
        "https://hsbc-dashboard.netlify.app"
    ]
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_CLIENT_ID: str = os.getenv("FIREBASE_CLIENT_ID", "")
    FIREBASE_PRIVATE_KEY_ID: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    FIREBASE_AUTH_URI: str = os.getenv("FIREBASE_AUTH_URI", "")
    FIREBASE_TOKEN_URI: str = os.getenv("FIREBASE_TOKEN_URI", "")
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "")
    FIREBASE_CLIENT_X509_CERT_URL: str = os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "")
    FIREBASE_UNIVERSE_DOMAIN: str = os.getenv("FIREBASE_UNIVERSE_DOMAIN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hsbc_dashboard.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "104857600"))
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
    MAX_ROWS_PREVIEW: int = 1000
    CHUNK_SIZE: int = 10000
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    LOG_LEVEL: str = "INFO"
    class Config:
        env_file = ".env"
        extra = Extra.ignore

settings = Settings() 
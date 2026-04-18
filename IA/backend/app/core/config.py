from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "PriceAI - Analysis System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "79632488c9f59b66929e46a74659f8ed571344605963955b55288921a28a2569")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        case_sensitive = True

settings = Settings()

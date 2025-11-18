from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "complaint_management"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ESCALATION_CHECK_INTERVAL_MINUTES: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

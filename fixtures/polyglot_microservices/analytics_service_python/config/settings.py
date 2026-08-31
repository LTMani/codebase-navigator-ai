from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "navigator-analytics-service"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8084
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/analytics_db"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5000"]
    BATCH_SIZE: int = 500
    FORECAST_HORIZON_DAYS: int = 30
    MODEL_CONFIDENCE_THRESHOLD: float = 0.85

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

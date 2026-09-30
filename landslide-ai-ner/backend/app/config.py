"""
Application configuration using pydantic-settings.
All values can be overridden via environment variables or a .env file.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql://postgres:password@localhost:5432/landslide_ner"
    )

    # ── Cache / Queue ────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT Auth ─────────────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production-super-secret-key-12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # ── IMD Weather API ──────────────────────────────────────────────────────
    IMD_API_KEY: str = ""
    IMD_API_BASE_URL: str = "https://api.imd.gov.in"

    # ── Satellite API ────────────────────────────────────────────────────────
    SATELLITE_API_KEY: str = ""
    SATELLITE_API_URL: str = ""

    # ── SMS Gateway ──────────────────────────────────────────────────────────
    SMS_API_KEY: str = ""
    SMS_API_URL: str = ""

    # ── Email ────────────────────────────────────────────────────────────────
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@landslide-ner.gov.in"

    # ── Object Storage ───────────────────────────────────────────────────────
    STORAGE_BUCKET: str = ""
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""

    # ── App Metadata ─────────────────────────────────────────────────────────
    APP_NAME: str = "Landslide AI NER"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Simulation / Demo mode ───────────────────────────────────────────────
    SIMULATION_MODE: bool = True
    SIMULATION_SEED: int = 42

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # ── File Storage ─────────────────────────────────────────────────────────
    MEDIA_DIR: str = "media"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton instance — import this everywhere
settings = Settings()

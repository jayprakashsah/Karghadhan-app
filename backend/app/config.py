"""
app/config.py
Centralised settings loaded from environment variables / .env file.
Uses Pydantic v2 BaseSettings for strict type-checking and validation.
"""
from __future__ import annotations

from functools import lru_cache
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Supabase
    # ------------------------------------------------------------------
    SUPABASE_URL: str = "https://mock.supabase.co"
    SUPABASE_KEY: str = "mock-key"                       # anon / public key
    SUPABASE_SERVICE_ROLE_KEY: str = "mock-key"          # service-role secret (bypasses RLS)
    DATABASE_URL: str = ""                       # PostgreSQL connection string

    # Alternative new Supabase naming conventions support
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""

    # ------------------------------------------------------------------
    # AI / LLM
    # ------------------------------------------------------------------
    GEMINI_API_KEY: str = "mock-gemini-key"
    OPENAI_API_KEY: str = ""                     # optional fallback

    # ------------------------------------------------------------------
    # Identity Verification / KYC Gateway
    # ------------------------------------------------------------------
    KYC_GATEWAY_URL: str = ""                    # e.g., https://sandbox.setu.co
    KYC_GATEWAY_API_KEY: str = ""                 # API key for the KYC gateway
    FACE_MATCH_THRESHOLD: float = 0.40           # cosine distance threshold
    FACE_MATCH_MODEL: str = "VGG-Face"           # DeepFace model name

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_ENV: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def resolve_keys(self) -> Settings:
        # Map new Supabase client key names to legacy names if legacy is empty
        if not self.SUPABASE_KEY and self.SUPABASE_PUBLISHABLE_KEY:
            self.SUPABASE_KEY = self.SUPABASE_PUBLISHABLE_KEY
        if not self.SUPABASE_SERVICE_ROLE_KEY and self.SUPABASE_SECRET_KEY:
            self.SUPABASE_SERVICE_ROLE_KEY = self.SUPABASE_SECRET_KEY

        # Fallback if somehow still missing
        if not self.SUPABASE_KEY:
            self.SUPABASE_KEY = "mock-key"
        if not self.SUPABASE_SERVICE_ROLE_KEY:
            self.SUPABASE_SERVICE_ROLE_KEY = "mock-key"

        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()  # type: ignore[call-arg]

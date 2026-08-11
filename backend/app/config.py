from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    db_password: str = "change_me"
    database_url: str = ""
    supabase_jwt_secret: str = "dev-secret-change-in-production"
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    public_url: str = "http://localhost:8000"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    fireworks_api_key: Optional[str] = None
    whatsapp_api_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_verify_token: str = "hermes_verify"
    telegram_bot_token: Optional[str] = None
    resend_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    encryption_key: str = "0" * 64
    default_primary_model: str = "claude-sonnet-4-2026"
    default_backup_model: str = "accounts/fireworks/models/deepseek-v4"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://hermes:{self.db_password}@postgres:5432/hermes"

settings = Settings()

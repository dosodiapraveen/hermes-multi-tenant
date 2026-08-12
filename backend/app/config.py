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
    telegram_webhook_secret: Optional[str] = None  # Secret token for webhook verification
    resend_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None
    encryption_key: str = "0" * 64
    default_primary_model: str = "claude-sonnet-4-2026"
    default_backup_model: str = "accounts/fireworks/models/deepseek-v4"
    admin_email: str = "admin@hermes.io"
    admin_password_hash: Optional[str] = None  # Set to bcrypt hash of admin password
    allowed_origins: str = "http://localhost:5173,https://beprepared.dev,https://www.beprepared.dev"  # Comma-separated list of allowed origins

    # Logging and monitoring
    sentry_dsn: Optional[str] = None  # Sentry DSN for error tracking
    sentry_environment: str = "development"  # Environment name (development, staging, production)
    sentry_traces_sample_rate: float = 0.1  # Sample rate for performance monitoring (10%)
    log_level: str = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    json_logs: bool = True  # Whether to output logs in JSON format

    # Cookie-based authentication (Phase 2)
    cookie_secure: bool = True  # Set to False for local development without HTTPS
    cookie_domain: Optional[str] = None  # Cookie domain (e.g., .yourdomain.com for subdomain sharing)
    enforce_csrf: bool = True  # Set to False during migration testing

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://hermes:{self.db_password}@postgres:5432/hermes"

settings = Settings()

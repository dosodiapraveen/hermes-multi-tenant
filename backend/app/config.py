from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional
import secrets
import warnings

class Settings(BaseSettings):
    db_password: str = "change_me"
    database_url: str = ""
    # SECURITY: JWT secret MUST be set via environment variable in production
    # The validator below will raise an error if using default in non-dev environment
    supabase_jwt_secret: str = ""
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
    # SECURITY: Encryption key MUST be set via environment variable in production
    encryption_key: str = ""
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

    @model_validator(mode='after')
    def validate_security_settings(self):
        """Validate critical security settings are configured for production."""
        is_dev = self.public_url.startswith("http://localhost") or self.sentry_environment == "development"

        # Generate secure defaults for development, warn/error for production
        if not self.supabase_jwt_secret:
            if is_dev:
                # Generate a random secret for development
                object.__setattr__(self, 'supabase_jwt_secret', secrets.token_urlsafe(32))
                warnings.warn("Using auto-generated JWT secret for development. Set SUPABASE_JWT_SECRET in production.", stacklevel=2)
            else:
                raise ValueError("SUPABASE_JWT_SECRET must be set in production environment")

        if not self.encryption_key or len(self.encryption_key) < 32:
            if is_dev:
                # Generate a random encryption key for development
                object.__setattr__(self, 'encryption_key', secrets.token_hex(32))
                warnings.warn("Using auto-generated encryption key for development. Set ENCRYPTION_KEY in production.", stacklevel=2)
            else:
                raise ValueError("ENCRYPTION_KEY must be set to at least 32 characters in production environment")

        return self

    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://hermes:{self.db_password}@postgres:5432/hermes"

settings = Settings()

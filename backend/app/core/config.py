"""
Centralized application configuration.
All environment-dependent values live here so nothing is hardcoded
elsewhere in the codebase (per ARCHITECTURE.md: "No hardcoded data").
"""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT_JWT_SECRET = "dev-secret-key-change-in-production"
_INSECURE_DEFAULT_SECRET = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "EvoFit AI"
    API_V1_PREFIX: str = ""

    # ENVIRONMENT controls dev/prod behavior switches (docs exposure, debug
    # error detail, HSTS header, secret validation, etc). DEBUG is a
    # secondary escape hatch that can be forced independently (e.g. verbose
    # logging on a prod-like staging box).
    ENVIRONMENT: str = "development"  # "development" | "staging" | "production"
    DEBUG: bool = True

    # --- Database ---------------------------------------------------------
    # SQLite locally, PostgreSQL in production. No application code branches
    # on this beyond database/session.py, which only inspects the URL scheme.
    DATABASE_URL: str = "sqlite:///./evofit.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # --- Auth / JWT ---------------------------------------------------------
    JWT_SECRET_KEY: str = _INSECURE_DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    # Short-lived access token; long-lived refresh token used to mint new
    # access tokens without forcing re-login. See core/security.py.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Generic app secret (kept distinct from the JWT signing key so the two
    # can be rotated independently).
    SECRET_KEY: str = _INSECURE_DEFAULT_SECRET

    # --- AI providers ---------------------------------------------------------
    # Optional and inert today. The app runs entirely on the built-in
    # RuleBasedProvider and makes no network calls to either API; these are
    # read only so a future ClaudeProvider/ChatGPTProvider can be switched on
    # via AI_PROVIDER later without any code changes. Neither key is required.
    CLAUDE_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    AI_PROVIDER: str = "rule_based"  # reserved for future use; only "rule_based" is implemented

    # --- CORS / hosts ---------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:5173"
    TRUSTED_HOSTS: str = "*"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # --- Rate limiting ---------------------------------------------------------
    RATE_LIMIT_ENABLED: bool = True
    AUTH_RATE_LIMIT: str = "10/minute"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """
        Fail fast on startup rather than silently running production with
        the placeholder dev secrets baked into source control.
        """
        if self.is_production:
            if self.JWT_SECRET_KEY == _INSECURE_DEFAULT_JWT_SECRET:
                raise ValueError(
                    "JWT_SECRET_KEY must be set to a unique secret when ENVIRONMENT=production"
                )
            if self.SECRET_KEY == _INSECURE_DEFAULT_SECRET:
                raise ValueError(
                    "SECRET_KEY must be set to a unique secret when ENVIRONMENT=production"
                )
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError(
                    "DATABASE_URL must point to PostgreSQL when ENVIRONMENT=production"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

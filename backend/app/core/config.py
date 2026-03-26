from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://jobuser:jobpass@localhost:5432/jobassist"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_scheme(cls, v: str) -> str:
        # Railway (and many PaaS) provide postgres:// or postgresql:// — SQLAlchemy needs +psycopg2
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File storage (local volume — Railway mounts this as a persistent volume)
    STORAGE_PATH: str = "/app/uploads"

    # AI provider
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # AI spend control
    AI_ENABLED: bool = True
    AI_MAX_REQUESTS_PER_DAY: int = 15
    AI_MAX_CV_CHARS: int = 6000
    AI_MAX_JOB_CHARS: int = 4000

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "text" = dev pretty output, "json" = production


settings = Settings()

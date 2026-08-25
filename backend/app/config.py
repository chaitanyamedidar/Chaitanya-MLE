from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    jwt_secret: str = "change-me-in-local-dev"
    jwt_expire_minutes: int = 720
    database_url: str = "sqlite:///./app.db"
    demo_email: str = "demo@quantiphi.dev"
    demo_password: str = "Demo@123"


settings = Settings()

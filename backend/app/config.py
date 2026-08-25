from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    jwt_secret: str = "change-me-in-local-dev"
    jwt_expire_minutes: int = 720
    database_url: str = "sqlite:///./app.db"


settings = Settings()

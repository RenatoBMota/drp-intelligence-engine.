from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DRP Intelligence Engine"
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://drp:drp@localhost:5432/drp"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()


from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    app_name: str = "NagrikAI API"

    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_db: str = "nagrikai"

    jwt_secret: str
    jwt_expire_minutes: int = 60

    frontend_origins: str = (
        "http://127.0.0.1:5500,http://localhost:5500"
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            item.strip()
            for item in self.frontend_origins.split(",")
            if item.strip()
        ]


settings = Settings()

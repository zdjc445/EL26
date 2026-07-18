from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TIME_", extra="forbid")

    environment: Literal["local", "test", "ci", "staging", "production"] = "local"
    build_sha: str = "development"

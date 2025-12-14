"""Configuration settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional



class Settings(BaseSettings):
    database_url: str = "sqlite:///./bot_gpt.db"
    groq_api_key: Optional[str] = None
    llm_model: str = "llama-3.3-70b-versatile"
    llm_max_tokens: int = 1024
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"   # 🔑 THIS IS THE KEY FIX
    )

settings = Settings()

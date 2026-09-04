"""
VerityMesh Configuration
Load settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://veritymesh:veritymesh_dev@localhost:5432/veritymesh"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- LLM Provider (Google Gemini) ---
    GOOGLE_API_KEY: str = ""

    # --- Web Search (Tavily) ---
    TAVILY_API_KEY: str = ""

    # --- Backend ---
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # --- Embedding ---
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSIONS: int = 768

    # --- LLM ---
    LLM_MODEL: str = "gemini-3.6-flash"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]


settings = Settings()

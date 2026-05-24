"""Application configuration from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file explicitly
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
        case_sensitive=False,
    )

    hf_dataset_id: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        validation_alias="HF_DATASET_ID",
    )
    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")
    llm_model: str = Field(default="groq-chat-1", validation_alias="LLM_MODEL")
    llm_base_url: str | None = Field(
        default=None,
        validation_alias="LLM_BASE_URL",
        description="Optional OpenAI-compatible or groq-compatible API base URL.",
    )
    llm_temperature: float = Field(default=0.3, validation_alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=1200, validation_alias="LLM_MAX_TOKENS")
    llm_timeout_seconds: float = Field(default=60.0, validation_alias="LLM_TIMEOUT_SECONDS")
    max_candidates: int = Field(default=20, validation_alias="MAX_CANDIDATES")
    top_k: int = Field(default=5, validation_alias="TOP_K")
    budget_low_max: int = Field(
        default=300,
        validation_alias="BUDGET_LOW_MAX",
        description="Max cost (for two) for 'low' tier, inclusive.",
    )
    budget_medium_max: int = Field(
        default=600,
        validation_alias="BUDGET_MEDIUM_MAX",
        description="Max cost (for two) for 'medium' tier, inclusive.",
    )
    parquet_cache_path: str = Field(
        default="data/restaurants.parquet",
        validation_alias="PARQUET_CACHE_PATH",
    )
    use_parquet_cache: bool = Field(default=True, validation_alias="USE_PARQUET_CACHE")

    @property
    def budget_thresholds(self) -> dict[str, int]:
        return {"low_max": self.budget_low_max, "medium_max": self.budget_medium_max}


@lru_cache
def get_settings() -> Settings:
    return Settings()

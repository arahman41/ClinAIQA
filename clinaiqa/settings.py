from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_REQUIRED_IN_PROD = ("anthropic_api_key", "database_url", "database_url_sync")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    database_url: str = ""
    database_url_sync: str = ""
    app_env: str = "development"
    log_level: str = "INFO"

    # Retrieval (Layer 1)
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    grounding_threshold: float = 0.70  # cosine similarity below this = ungrounded
    retrieval_top_k: int = 5

    # Synthetic data split
    split_seed: int = 42
    heldout_fraction: float = 0.25

    @model_validator(mode="after")
    def _check_required(self) -> "Settings":
        if self.app_env == "development":
            return self
        missing = [f for f in _REQUIRED_IN_PROD if not getattr(self, f)]
        if missing:
            raise ValueError(f"Missing required settings for app_env={self.app_env!r}: {missing}")
        return self


settings = Settings()

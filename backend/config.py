"""
SK AgentCorp — Configuration Module

Central configuration management using Pydantic Settings.
All config values are read from environment variables or .env file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────
    app_name: str = "SK AgentCorp"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./sk-agentcorp.db"

    # ── LLM Providers ────────────────────────────────────────────────
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    groq_api_key: str = ""
    xai_api_key: str = ""

    default_llm_provider: Literal["openai", "anthropic", "ollama", "groq", "xai"] = "openai"
    default_llm_model: str = "gpt-4o"

    # ── Security ─────────────────────────────────────────────────────
    api_secret_key: str = "change-me-to-a-random-string"
    api_keys: str = "sk-agentcorp-dev-key"  # Comma-separated

    # ── Heartbeat ────────────────────────────────────────────────────
    heartbeat_interval_seconds: int = 300  # 5 minutes

    # ── Budget ───────────────────────────────────────────────────────
    global_budget_cap_usd: float = 1000.00
    per_task_budget_cap_usd: float = 50.00

    # ── Anti-Stuck ───────────────────────────────────────────────────
    max_task_retries: int = 3
    task_timeout_seconds: int = 600  # 10 minutes

    # ── Logging ──────────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Paths ────────────────────────────────────────────────────────
    roles_dir: str = str(Path(__file__).parent.parent / "roles")
    templates_dir: str = str(Path(__file__).parent.parent / "templates")
    data_dir: str = str(Path(__file__).parent.parent / "data")

    @property
    def api_key_list(self) -> list[str]:
        """Parse comma-separated API keys into a list."""
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()

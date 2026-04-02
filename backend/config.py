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

    @property
    def default_llm_provider(self) -> str:
        """Load the default provider from JSON config."""
        path = Path(__file__).parent / "llm_configs" / "default_model.json"
        if path.exists():
            try:
                import json
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f).get("provider", "openai")
            except Exception:
                pass
        return "openai"

    @property
    def default_llm_model(self) -> str:
        """Load the default model from JSON config."""
        path = Path(__file__).parent / "llm_configs" / "default_model.json"
        if path.exists():
            try:
                import json
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f).get("model", "gpt-5.4-pro")
            except Exception:
                pass
        return "gpt-5.4-pro"

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

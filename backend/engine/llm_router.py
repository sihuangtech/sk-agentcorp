"""
SK AgentCorp — LLM Router

Routes LLM calls to the appropriate provider (OpenAI, Anthropic, Ollama, Groq, xAI).
Supports per-agent model overrides and automatic fallback.
"""

import json
import logging
from pathlib import Path
from typing import Any

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)

# Cache initialized LLM instances
_llm_cache: dict[str, BaseChatModel] = {}

LLM_CONFIGS_DIR = Path(__file__).parent.parent / "llm_configs"

def load_api_keys() -> dict:
    """Load the unified API keys from api_keys.json."""
    keys_path = LLM_CONFIGS_DIR / "api_keys.json"
    if not keys_path.exists():
        return {}
    try:
        with open(keys_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load API keys: {e}")
        return {}

def load_provider_config(provider: str) -> dict:
    """Load the JSON configuration for a specific LLM provider."""
    paths_to_check = [
        LLM_CONFIGS_DIR / "global" / f"{provider}.json",
        LLM_CONFIGS_DIR / "china" / f"{provider}.json",
    ]
    
    for config_path in paths_to_check:
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config for {provider} at {config_path}: {e}")
                return {}
    return {}

def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Get an LLM instance for the specified provider and model.

    Reads keys from api_keys.json and configuration from provider JSON files.
    Caches instances for reuse.
    """
    provider = provider or "openai"
    config = load_provider_config(provider)
    api_keys = load_api_keys()
    
    api_key = api_keys.get(provider)
    api_base = config.get("api_base")
    model = model or config.get("default_model", "gpt-5.4-pro")

    cache_key = f"{provider}:{model}:{temperature}:{api_key}"
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    llm: BaseChatModel

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or "sk-placeholder",
            base_url=api_base if api_base and api_base != "https://api.openai.com/v1" else None,
            **kwargs,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key or "sk-ant-placeholder",
            base_url=api_base if api_base and api_base != "https://api.anthropic.com" else None,
            **kwargs,
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key or "AIza-placeholder",
            **kwargs,
        )

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model=model,
            temperature=temperature,
            base_url=api_keys.get("ollama") or api_base or "http://localhost:11434",
            **kwargs,
        )

    elif provider == "groq":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or "gsk-placeholder",
            base_url=api_base or "https://api.groq.com/openai/v1",
            **kwargs,
        )

    elif provider == "xai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or "xai-placeholder",
            base_url=api_base or "https://api.x.ai/v1",
            **kwargs,
        )

    elif provider in ["deepseek", "alibaba", "zhipu", "moonshot", "baichuan", "minimax", "stepfun", "sensetime"]:
        # Chinese models all provide OpenAI-compatible endpoints generally
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or f"{provider}-placeholder",
            base_url=api_base,
            **kwargs,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    _llm_cache[cache_key] = llm
    logger.info(f"Initialized LLM: {provider}/{model}")
    return llm


def clear_llm_cache() -> None:
    """Clear the LLM instance cache."""
    _llm_cache.clear()


# ── Provider availability check ──────────────────────────────────────

def get_available_providers() -> list[dict[str, str]]:
    """Return list of configured LLM providers with their status."""
    providers = []
    api_keys = load_api_keys()

    checks = [
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("google", "Google"),
        ("groq", "Groq"),
        ("xai", "xAI"),
        ("ollama", "Ollama (Local)"),
        ("deepseek", "DeepSeek"),
        ("alibaba", "Alibaba (Qwen)"),
        ("zhipu", "Zhipu AI (GLM)"),
        ("moonshot", "Moonshot (Kimi)"),
        ("baichuan", "Baichuan"),
        ("minimax", "MiniMax"),
        ("stepfun", "StepFun"),
        ("sensetime", "SenseTime (SenseNova)"),
    ]

    for provider_id, display_name in checks:
        config = load_provider_config(provider_id)
        # For ollama, it's configured if base_url is set in api_keys or config
        if provider_id == "ollama":
            is_configured = bool(api_keys.get("ollama") or config.get("api_base"))
        else:
            is_configured = bool(api_keys.get(provider_id))
            
        providers.append({
            "id": provider_id,
            "name": display_name,
            "configured": is_configured,
            "default_model": config.get("default_model", ""),
            "supported_models": config.get("supported_models", [])
        })

    return providers

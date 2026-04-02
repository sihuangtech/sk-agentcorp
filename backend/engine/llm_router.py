"""
SK AgentCorp — LLM Router

Routes LLM calls to the appropriate provider dynamically based on JSON config files.
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
    
    api_key = api_keys.get(provider) or None
    api_base = config.get("api_base")
    model = model or config.get("default_model", "gpt-5.4-pro")

    cache_key = f"{provider}:{model}:{temperature}:{api_key}"
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    llm: BaseChatModel

    # Standardize providers needing specific native clients
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base,
            **kwargs,
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key,
            **kwargs,
        )

    elif provider == "mistral":
        from langchain_mistralai import ChatMistralAI
        llm = ChatMistralAI(
            model=model,
            temperature=temperature,
            mistral_api_key=api_key,
            endpoint=api_base,
            **kwargs,
        )

    elif provider == "cohere":
        from langchain_cohere import ChatCohere
        llm = ChatCohere(
            model=model,
            temperature=temperature,
            cohere_api_key=api_key,
            base_url=api_base,
            **kwargs,
        )

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model=model,
            temperature=temperature,
            base_url=api_base,
            **kwargs,
        )

    else:
        # Fallback to OpenAI-compatible client for ALL other providers 
        # (OpenAI, DeepSeek, Alibaba, Zhipu, Moonshot, Baichuan, Groq, xAI, etc.)
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base,
            **kwargs,
        )

    _llm_cache[cache_key] = llm
    logger.info(f"Initialized LLM: {provider}/{model}")
    return llm


def clear_llm_cache() -> None:
    """Clear the LLM instance cache."""
    _llm_cache.clear()


# ── Provider availability check ──────────────────────────────────────

def _scan_folder(folder: Path, category: str, api_keys: dict) -> list[dict[str, Any]]:
    """Scan a config folder for provider JSONs and build their settings payload."""
    results = []
    if not folder.exists() or not folder.is_dir():
        return results
        
    for file in folder.glob("*.json"):
        provider_id = file.stem
        try:
            with open(file, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # Ollama is configured if a base_url exists. Everything else checks api_key field.
            if provider_id == "ollama":
                is_configured = bool(api_keys.get("ollama") or config.get("api_base"))
            else:
                is_configured = bool(api_keys.get(provider_id))
                
            # Pluck display name from config JSON, fallback to capitalized ID
            display_name = config.get("display_name", provider_id.capitalize())
            
            results.append({
                "id": provider_id,
                "name": display_name,
                "category": category,
                "configured": is_configured,
                "default_model": config.get("default_model", ""),
                "supported_models": config.get("supported_models", [])
            })
        except Exception as e:
            logger.error(f"Error parsing {file}: {e}")
            
    return results

def get_available_providers() -> list[dict[str, Any]]:
    """Dynamically scan config directories to list all supported LLM providers."""
    api_keys = load_api_keys()
    providers = []
    
    # Scan global directory
    global_dir = LLM_CONFIGS_DIR / "global"
    providers.extend(_scan_folder(global_dir, "Global", api_keys))
    
    # Scan china directory
    china_dir = LLM_CONFIGS_DIR / "china"
    providers.extend(_scan_folder(china_dir, "China", api_keys))
    
    return providers

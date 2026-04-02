# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-04-02

### Added

- **Global & China LLM Matrix**: Expanded out-of-the-box support to 22 LLM providers, splitting configs into `backend/llm_configs/global/` and `backend/llm_configs/china/`.
- **Top-Tier Provider Integration**: Added native JSON configurations and routing support for 2026-era models from OpenAI (GPT-5.4), Anthropic (Claude 4.6), Google (Gemini 3.1), xAI, Groq, Mistral AI, Cohere, DeepSeek, Alibaba, Zhipu AI, Moonshot, Baichuan, MiniMax, StepFun, SenseTime, Baidu, Tencent, ByteDance, iFLYTEK, 01.AI, and 360 Security.
- **Dynamic Routing Engine**: The LLM engine (`backend/engine/llm_router.py`) now features a completely decoupled architecture. It dynamically scans the file system for JSON configurations at runtime, automatically registering available providers without requiring any Python code modifications.
- **Unified Placeholder Safety**: Added robust handling for API keys alongside fallback tracking via `api_keys.json.example`.
- **Independent Default Modeling**: Added `default_model.json` to handle standard invocation behaviors dynamically.

### Changed

- **Zero-Env Secrets Policy**: Removed all API keys (e.g., `OPENAI_API_KEY`) and LLM properties (`DEFAULT_LLM_PROVIDER`, `DEFAULT_LLM_MODEL`) from the `.env` ecosystem to prevent accidental variable leaking.
- **Router Refactoring**: Rewrote `llm_router.py` to strip out massive `if-elif` blocks and hardcoded model logic in favor of generic LangChain OpenAI-compatible endpoints (`langchain_openai.ChatOpenAI`), except for providers utilizing specialized clients (Anthropic, Google, Ollama, Cohere, Mistral).
- **Settings Extraction**: System configurations in `backend/config.py` now use dynamic `@property` evaluation instead of rigid Pydantic environment mappings.
- **Git Security Upgrade**: Advanced masking via `.gitignore` to exclude real configurations (`api_keys.json`, `default_model.json`) while permitting `.example` schema files to assist future development teams.

### Removed

- **HardCoded Prompting**: Completely stripped internal codebase string-stuffed LLM system prompts (migrated completely to `backend/prompts/` text files during engine modularization).
- **Static Display Variables**: Purged GUI-specific text strings and variable defaults from the backend router, offloading `display_name` control directly to the JSON config specs.

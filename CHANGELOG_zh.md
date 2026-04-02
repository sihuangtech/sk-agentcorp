# 更新日志 (Changelog)

本项目所有的重大变更都将记录于此。

本日志的格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范构建，并严格遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html) 语义化版本控制。

## [0.0.1] - 2026-04-02

### ✨ 新增 (Added)

- **划区模型架构 (Global & China Matrix)**：重构了底层的配置文件系统，将国际大厂与国内厂商分立在 `backend/llm_configs/global/` 与 `backend/llm_configs/china/` 独立空间下。
- **全生态顶流接入**：预置了 22 家 2026 头部大模型 API 厂商的 JSON 配置，涵盖 OpenAI (GPT-5.4 时代), Anthropic (Claude 4.6), Google (Gemini 3.1), xAI, Groq, Mistral, Cohere，以及国内所有第一梯队诸如 DeepSeek, 阿里通义, 智谱 AI, 月之暗面 (Kimi), 百川智能, 阶跃星辰, 百度文心, 腾讯混元, 字节豆包等。
- **纯动态路由引擎**：重构了大模型路由分发中枢 (`backend/engine/llm_router.py`)，现在后端引擎会在启动时全自动扫描并挂载上述配置文件。**接入新模型厂商不再需要修改任何一行 Python 逻辑代码。**
- **默认模型配置化**：通过引入 `default_model.json`，为全系统 Agent 打造了脱离环境绑定的兜底大模型加载机制。
- **预置示例规范库**：配套增加了 `.example` 文件（如 `api_keys.json.example` 等），助力团队在无痛部署的同时掌控参数标准。

### 🚀 变更 (Changed)

- **Zero-Env 环境去密化**：彻底淘汰了对局域网及远端易泄漏的 `.env` 文件存放密钥的依赖。废除了如 `OPENAI_API_KEY`, `DEFAULT_LLM_MODEL` 等相关环境变量设定。
- **路由兼容性泛化**：拔除了原 `llm_router.py` 中臃肿的 `if-elif` 厂商判断语句。现在除了 Anthropic、Google、Cohere 等具备深度底层隔离性的外端，其余 95% 全量通过默认 `ChatOpenAI` 类实现透明的 API 兼容式网关转发。
- **底层解耦 (Settings 剥离)**：修改了 `backend/config.py`，使之剥离对 Pydantic `BaseSettings` 的依赖僵化，将所需设定重构为动态读取的 `@property` 计算属性。
- **安全拦截升级**：调整了项目根目录的 `.gitignore` 规则以拦截所有真实的 JSON 涉密凭证文件，杜绝源码外泄风险。

### 🗑️ 移除 (Removed)

- **Python 内嵌提示词废弃**：将业务 Workflow 下所有的 Prompt 提示签全面剥离进了专设的 `backend/prompts/` 外部文本夹，实现了逻辑层与语言层的剥离。
- **硬编码展示字符斩首**：将包含控制台下拉框在内的所有 `display_name` 字段显示逻辑抽离至 JSON 配置中定夺，摒弃了代码包死字符串的做法。

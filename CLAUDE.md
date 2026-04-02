# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SK AgentCorp is a "Zero-Human Company Operating System" — a platform for running autonomous AI agent companies 24/7. It uses LangGraph for stateful workflows, CrewAI for agent orchestration, and FastAPI for the backend. The frontend is a React 19 dashboard with Tailwind CSS.

## Commands

### Backend (Python)

```bash
# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn backend.main:app --reload --port 8000

# Run via CLI
sk-agentcorp start --reload

# Lint and type check
ruff check .
mypy backend/
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev      # Development server at localhost:5173
npm run build    # Production build
npm run lint     # ESLint
```

### Docker

```bash
docker-compose up -d --build
```

## Architecture

### Backend Structure (`backend/`)

- **`main.py`** — FastAPI entry point, registers routers, manages lifespan (DB init, heartbeat startup)
- **`config.py`** — Pydantic Settings loaded from `.env` (LLM providers, database, budget caps, anti-stuck params)
- **`database.py`** — Async SQLAlchemy with SQLite (default) or PostgreSQL support
- **`models/`** — SQLAlchemy ORM models (Company, Agent, Task, Budget, Audit)
- **`schemas/`** — Pydantic schemas for API request/response validation
- **`services/`** — Business logic layer (CRUD operations, audit logging)
- **`routers/`** — FastAPI endpoints (companies, agents, tasks, budget, dashboard, websocket)

### Core Engine (`backend/engine/`)

- **`workflow.py`** — LangGraph StateGraph for task execution: `plan → execute → validate → deliver`. Includes retry logic and checkpoint persistence via `MemorySaver`.
- **`llm_router.py`** — Multi-provider LLM routing (OpenAI, Anthropic, Ollama, Groq, xAI). Caches instances per provider/model.
- **`anti_stuck.py`** — Monitors stuck tasks/agents. Handles timeout detection, automatic retry (up to `max_retries`), supervisor fallback escalation, and agent reset.
- **`heartbeat.py`** — APScheduler-driven periodic task that wakes up the company, processes queued tasks, and runs anti-stuck scans.
- **`shared_memory.py`** — Company-wide knowledge sharing between agents
- **`crew_builder.py`** — Dynamically assembles CrewAI crews from role definitions

### Roles System (`roles/`)

YAML-based agent definitions organized by department (`executive/`, `engineering/`, `marketing/`, etc.). Each role specifies `name`, `role`, `goal`, `backstory`, `skills`, and `tools`. New roles are added by creating a YAML file in the appropriate department subdirectory.

### Frontend Structure (`frontend/src/`)

- **`main.tsx`** — Entry point
- **`App.tsx`** — React Router setup with routes for Overview, OrgChart, Kanban, Budget, Audit pages
- **`context/ShellContext.tsx`** — Global state (WebSocket connection, company data)
- **`components/layout/`** — Sidebar and Header components
- **`pages/`** — Route page components (OverviewPage, OrgChartPage with React Flow, KanbanPage, BudgetPage, AuditPage)

### CLI (`cli/main.py`)

Typer-based CLI with commands: `init`, `start`, `dashboard`, `status`, `heartbeat`.

## Key Patterns

### Task Workflow State Machine

Tasks flow through: `backlog → queued → in_progress → review → done` (or `failed`). The LangGraph workflow handles internal execution states: `planning → executing → validating → delivering`. Failed validation triggers retry; after `max_retries`, tasks escalate to `fallback_agent_id` or fail permanently.

### Anti-Stuck Engine

Runs during each heartbeat cycle. Detects tasks that have exceeded `task_timeout_seconds` or agents stuck in `working` status without an active task. Automatically retries, escalates to supervisor, or marks as permanently failed with audit logging.

### LLM Configuration

Provider/model can be set globally in `.env` (`DEFAULT_LLM_PROVIDER`, `DEFAULT_LLM_MODEL`) or overridden per-agent in the database. The `llm_router.py` caches LLM instances by `(provider, model, temperature)` tuple.

## Environment Setup

Copy `.env.example` to `.env` and configure at minimum one LLM provider API key. Key variables:

- `DATABASE_URL` — SQLite path or PostgreSQL connection string
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` — LLM provider keys
- `DEFAULT_LLM_PROVIDER` / `DEFAULT_LLM_MODEL` — Default model for agents
- `HEARTBEAT_INTERVAL_SECONDS` — How often the system wakes up (default 300s)
- `MAX_TASK_RETRIES` — Retries before fallback (default 3)
- `TASK_TIMEOUT_SECONDS` — Task timeout before anti-stuck intervention (default 600s)

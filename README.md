# SK AgentCorp 🏢

> Next-Generation Zero-Human Company Operating System

![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/React-19-blue.svg)

SK AgentCorp is the most reliable zero-human company platform built for the 2026 era. Its goal is to let you solely act as the "Board of Directors & CEO" (responsible for high-level decision-making and budget approval), while an entirely autonomous professional Crew of AI Agents runs the company 24/7 without human intervention.

Addressing the pain points of existing autonomous platforms (such as infinite loops, context loss, and coordination failures), SK AgentCorp introduces **strong state-persistence**, **consensus-shared memory**, and a powerful **Anti-Stuck Engine**.

---

## 🌟 Core Concepts & Features

- **24/7 Autonomous Heartbeat**: Built-in APScheduler mechanism continuously scans queues and awakens workflows at configured intervals.
- **Modern React 19 Dashboard**: Gorgeous dark mode, drag-and-drop structural organization charts (React Flow), real-time Kanban boards, active fund burn-rate monitoring, and immutable auditing logs.
- **Robust Anti-Stuck Engine**: Automatically retries tasks with structural validation verification after failures (up to 3 times); cascades fallbacks to Supervisor Agents for proactive re-planning upon critical faults.
- **LangGraph + Checkpoint Persistence**: Fully stateful workflows persisting directly to disk, supporting Time-Travel debugging and memory sharing, guaranteeing zero context loss over extremely long horizons.
- **Drop-in Configuration Ecosystem (Zero-Env Strategy)**: Completely decoupled configuration using flat JSON files (`backend/llm_configs/`), natively supporting 22 top-tier 2026 AI providers (OpenAI, Anthropic, Google, DeepSeek, Qwen/Alibaba, etc) with zero code modification.
- **Plug-and-Play YAML Agent Library**: Pre-loaded with 50+ granular YAML role definitions (CEO, Engineers, Marketing Strategists) built to dynamically assemble Crews on demand.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph "Board of Directors (React Dashboard)"
        UI[Beautiful Web UI]
        Vis[Org Chart & Kanban]
        Controls[Goal Setting & Budgets]
    end

    subgraph "SK AgentCorp Backend System (FastAPI)"
        API[RESTful APIs]
        WS[WebSocket Real-time IO]
        DB[(SQLite / Postgres)]
        Heartbeat[⏰ 24/7 Heartbeat<br/>(APScheduler)]
    end

    subgraph "SK AgentCorp Core Engine (LangGraph)"
        Controller[CEO/Supervisor Router Center]
        State[💾 Consensus Shared Memory<br/>& Checkpointer]
        WorkerPool[Built-in 50+ Agents<br/>(CrewAI Base)]
        
        Graph{Stateful Workflow}
        Graph -->|Delegate Task| BuildCrew[Dynamic Crew Assembly]
        BuildCrew --> Execute[Task Execution]
        Execute --> Verify{Structured Output Verification}
        Verify -->|Fail/Timeout| Retry[Auto-Retry (Max 3)]
        Retry -->|Persistent Fail| Fallback[Fallback to Supervisor Planner]
        Verify -->|Success| DB_Record[Record Progress & Update Org Knowledge]
        Verify -->|Over-Budget/Approval| Human[Pause & Request Board Approval]
    end

    UI <--> API
    UI <--> WS
    Controls --> API
    API <--> DB
    
    Heartbeat -->|Interval Wakeup| Controller
    Controller <--> Graph
    State <--> Graph
    Graph <--> WorkerPool
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+ & pnpm (or npm/yarn)
- Docker & Docker Compose (for single-command deployments)

### Local Development Setup

#### 1. Clone & Init Configuration

```bash
git clone https://github.com/sihuangtech/sk-agentcorp.git
cd sk-agentcorp

# Config the environment and LLM Router configs
cp .env.example .env
cp backend/llm_configs/api_keys.json.example backend/llm_configs/api_keys.json
cp backend/llm_configs/default_model.json.example backend/llm_configs/default_model.json
```

#### 2. Start Backend Engine

```bash
cd backend
pip install -r requirements.txt # (or uv pip install)
uvicorn main:app --reload --port 8000
```

#### 3. Start Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
```

### Docker One-Click Deployment

To launch the complete stack (including Database, Frontend, Backend):

```bash
docker-compose up -d --build
```

After startup:

- Access Dashboard: `http://localhost:3000`
- Access API Docs: `http://localhost:8000/docs`

---

## 👥 Adding Custom Roles

Agent roles are globally managed through `.yaml` configurations in the `roles/` directory.

1. Create a `.yaml` file inside the respective group array (e.g. `roles/engineering/devops_lead.yaml`).
2. Populate specific behavioral metrics:

   ```yaml
   name: "Content Strategist"
   role: "Content Strategy Lead"
   goal: "Develop high-converting content plans that align with our brand identity."
   backstory: "You are a seasoned content wizard who knows how to capture audiences..."
   skills:
     - SEO optimization
     - Copywriting
   tools:
     - SearchTool
     - ScrapeTool
   ```

3. The system's dynamic `CrewBuilder` component will natively parse and dispatch the new role upon next engine startup.

---

## 🗂️ Project Structure

- `backend/` - FastAPI Service, LangGraph Workflow Engine, Anti-Stuck Modules, JSON Routing Configs (`llm_configs/`)
- `frontend/` - React 19 + TypeScript + Vite interactive Dashboard Console
- `roles/` - Fine-grained granular YAML Agent Storage
- `cli/` - Central terminal tool kit (`sk-agentcorp init/start/dashboard`)

---

## 📜 License

This project relies on the [CC BY-NC 4.0](LICENSE) License — Free for open, non-commercial purposes, but restricted from unauthorized enterprise resale.

# SK AgentCorp 🏢

> 下一代零人公司操作系统 (Zero-Human Company Operating System)

![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/React-19-blue.svg)

SK AgentCorp 是 2026 年最可靠的零人公司平台。它的目标是让你只需担任“董事会与 CEO”的角色（负责高层决策和预算审批），整个公司由多个 AI Agent 组成的专业 Crew 团队 24/7 自主运行，几乎无需人工干预。

针对现有平台（如 Paperclip, Auto-Company）的卡死、上下文丢失、协调失败等痛点，SK AgentCorp 引入了**强状态持久化**、**共识共享内存**与强大的**防卡死引擎 (Anti-Stuck Engine)**。

---

## 🌟 核心理念与特性

- **24/7 全自动心跳运行**：内置 APScheduler 驱动心跳机制，系统持续扫描队列并定期唤醒工作流。
- **现代化 React 19 Dashboard**：美观的深色模式、拖拽式组织架构图 (React Flow)、实时看板 (Kanban)、资金消耗与预算监控、不可变审计日志。
- **强大的防卡死引擎 (Anti-Stuck)**：任务执行失败后自动重试（最多3次），结构化输出验证；多次失败则 Fallback 至主管级 Agent 请求重新规划。
- **LangGraph + Checkpoint 持久化**：工作流有状态且全量落盘，支持时间旅行 (Time-Travel) 调试和共享内存，保证长周期运行中上下文绝对不丢失。
- **即插即用的专家库**：预置 50+ 个基于 YAML 的精细化角色（CEO, 各种工程师, 营销专家等），支持轻松定义并自带 3 个“公司模板”。
- **多模型支持 (LLM Agnostic)**：支持 OpenAI, Anthropic, Google, Grok 等主流提供商。

---

## 🏗️ 系统架构图

```mermaid
graph TD
    subgraph "董事会 / 用户控制台 (React Dashboard)"
        UI[美观易用的 Web UI]
        Vis[Org Chart & Kanban]
        Controls[目标设定与预算分配]
    end

    subgraph "SK AgentCorp Backend System (FastAPI)"
        API[RESTful APIs]
        WS[WebSocket 实时通讯]
        DB[(SQLite / Postgres)]
        Heartbeat[⏰ 24/7 Heartbeat<br/>(APScheduler)]
    end

    subgraph "SK AgentCorp 核心引擎 (LangGraph)"
        Controller[CEO/主管 决策路由中心]
        State[💾 共识共享内存<br/>& Checkpointer]
        WorkerPool[预置 50+ 专业 Agent 库<br/>(CrewAI Base)]
        
        Graph{Stateful Workflow}
        Graph -->|委派任务| BuildCrew[动态组建 Crew]
        BuildCrew --> Execute[执行具体任务]
        Execute --> Verify{结构化有效性验证}
        Verify -->|失败/超时| Retry[自动重试 (最大3次)]
        Retry -->|仍然失败| Fallback[Fallback 至主管重新规划]
        Verify -->|成功| DB_Record[记录进展与更新架构知识]
        Verify -->|超预算/需人类介入| Human[暂停并请求董事会审批]
    end

    UI <--> API
    UI <--> WS
    Controls --> API
    API <--> DB
    
    Heartbeat -->|按时唤醒与扫描| Controller
    Controller <--> Graph
    State <--> Graph
    Graph <--> WorkerPool
```

---

## 🚀 快速开始

### 依赖要求

- Python 3.11+
- Node.js 20+ & pnpm (或 npm/yarn)
- Docker & Docker Compose (用于一键部署)

### 本地开发运行方法

#### 1. 克隆与初始化环境

```bash
git clone https://github.com/sihuangtech/sk-agentcorp.git
cd SK AgentCorp

# 复制环境变量
cp .env.example .env
```

#### 2. 启动后端引擎

```bash
# 推荐使用 uv 或 poetry
cd backend
pip install -r requirements.txt # 或 uv pip install
uvicorn main:app --reload --port 8000
```

#### 3. 启动前端 Dashboard

```bash
cd frontend
npm install
npm run dev
```

### Docker 一键部署

如果您希望在服务器上一次性拉起全套系统（包含数据库等）：

```bash
docker-compose up -d --build
```

系统启动后：

- 访问 Dashboard: `http://localhost:3000`
- 访问 API Docs: `http://localhost:8000/docs`

---

## 👥 如何添加新角色？

角色的配置文件统一放在 `roles/` 目录下，按部分（如 `executive`, `engineering`）分类，格式要求严格。

1. 在 `roles/[department]/` 新建 `.yaml` 文件（例如 `my_custom_role.yaml`）。
2. 在文件中填入标准字段：

   ```yaml
   name: "Content Strategist"
   role: "Content Strategy Lead"
   goal: "Develop high-converting content plans that align with our brand identity."
   backstory: "You are a seasoned content wizard who knows how to capture audiences..."
   skills:
     - SEO optimization
     - Copywriting
     - Trend analysis
   tools:
     - SearchTool
     - ScrapeTool
   ```

3. 系统会在启动时，以及动态运行 `CrewBuilder` 时自动扫描并支持调度此新角色。

---

## 🗂️ 目录结构预览

- `backend/` - FastAPI 服务, LangGraph 工作流引擎, 防卡死模块
- `frontend/` - React 19 + TypeScript + Vite, 包含 Dashboard 界面
- `roles/` - 细粒度的 YAML 角色存储库
- `cli/` - 命令行管理工具 (`sk-agentcorp init/start/dashboard`)

---

## 📜 许可协议

本项目采用 [CC BY-NC 4.0](LICENSE) 许可协议 — 允许非商业用途，禁止商业使用。

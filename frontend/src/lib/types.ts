// ═══════════════════════════════════════════════════════════════════════
//  SK AgentCorp TypeScript Types — Matches backend Pydantic schemas exactly
// ═══════════════════════════════════════════════════════════════════════

// ── Company ─────────────────────────────────────────────────────────

export interface CompanyCreate {
  name: string
  description?: string
  mission?: string
  vision?: string
  goals?: string[]
  budget_cap_usd?: number
  template_id?: string
}

export interface CompanyResponse {
  id: string
  name: string
  description: string
  mission: string
  vision: string
  goals: string[]
  budget_cap_usd: number
  budget_spent_usd: number
  is_active: boolean
  is_paused: boolean
  pause_reason: string
  template_id: string
  created_at: string
  updated_at: string
  last_heartbeat_at: string | null
  agent_count: number
  task_count: number
  active_task_count: number
}

export interface CompanyDashboardStats {
  total_companies: number
  active_companies: number
  total_agents: number
  active_agents: number
  total_tasks: number
  completed_tasks: number
  in_progress_tasks: number
  failed_tasks: number
  total_budget_spent: number
  total_budget_cap: number
}

// ── Agent ────────────────────────────────────────────────────────────

export interface AgentResponse {
  id: string
  company_id: string
  role_id: string
  name: string
  title: string
  department: string
  llm_provider: string
  llm_model: string
  status: string
  current_task_id: string | null
  status_message: string
  reports_to: string | null
  position_x: number
  position_y: number
  tasks_completed: number
  tasks_failed: number
  total_cost_usd: number
  is_active: boolean
  system_prompt: string
  tools: string[]
  backstory: string
  created_at: string
  updated_at: string
  last_active_at: string | null
}

// ── Task ─────────────────────────────────────────────────────────────

export interface TaskResponse {
  id: string
  company_id: string
  title: string
  description: string
  priority: string
  category: string
  status: string
  assigned_agent_id: string | null
  assigned_agent_name: string
  crew_id: string | null
  acceptance_criteria: string
  deliverables: string[]
  output: string
  output_quality_score: number | null
  retry_count: number
  max_retries: number
  timeout_seconds: number
  error_log: string
  fallback_agent_id: string | null
  thread_id: string | null
  checkpoint_id: string | null
  estimated_cost_usd: number
  actual_cost_usd: number
  kanban_column: string
  kanban_order: number
  requires_approval: boolean
  approval_status: string
  created_at: string
  updated_at: string
  started_at: string | null
  completed_at: string | null
}

// ── Budget ───────────────────────────────────────────────────────────

export interface BudgetEntryResponse {
  id: string
  company_id: string
  entry_type: string
  description: string
  amount_usd: number
  llm_provider: string
  llm_model: string
  tokens_input: number
  tokens_output: number
  task_id: string | null
  agent_id: string | null
  created_at: string
}

export interface BudgetSummary {
  company_id: string
  budget_cap_usd: number
  total_spent_usd: number
  remaining_usd: number
  utilization_pct: number
  is_over_budget: boolean
  entries_count: number
  cost_by_type: Record<string, number>
  cost_by_model: Record<string, number>
  daily_spend: Array<{ date: string; amount: number }>
}

// ── Audit ────────────────────────────────────────────────────────────

export interface AuditEntry {
  id: string
  event_type: string
  severity: string
  category: string
  actor_type: string
  actor_name: string
  message: string
  details: Record<string, any>
  task_id: string | null
  agent_id: string | null
  created_at: string
}

// ── WebSocket ────────────────────────────────────────────────────────

export interface WSMessage {
  type: string
  data?: any
  timestamp: string
  message?: string
}

// ── Role ─────────────────────────────────────────────────────────────

export interface RoleDefinition {
  id: string
  name: string
  title: string
  department: string
  category: string
  description: string
  system_prompt: string
  backstory: string
  responsibilities: string[]
  tools: string[]
  reports_to: string
  skills: string[]
}

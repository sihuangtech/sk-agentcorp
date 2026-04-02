import { create } from 'zustand'
import api from './api'
import type {
  CompanyResponse,
  CompanyDashboardStats,
  AgentResponse,
  TaskResponse,
  BudgetSummary,
  BudgetEntryResponse,
  AuditEntry,
} from './types'

// ═══════════════════════════════════════════════════════════════════════
//  SK AgentCorp Global Store — Single source of truth for all API data
// ═══════════════════════════════════════════════════════════════════════

interface PhantomStore {
  // ── State ──────────────────────────────────────────────────────────
  activeCompanyId: string | null
  companies: CompanyResponse[]
  dashboardStats: CompanyDashboardStats | null
  agents: AgentResponse[]
  tasks: TaskResponse[]
  budgetSummary: BudgetSummary | null
  budgetEntries: BudgetEntryResponse[]
  auditLogs: AuditEntry[]
  activityFeed: AuditEntry[]

  // Loading states
  loading: {
    companies: boolean
    stats: boolean
    agents: boolean
    tasks: boolean
    budget: boolean
    audit: boolean
    activity: boolean
  }

  // Error state
  error: string | null

  // ── Actions ────────────────────────────────────────────────────────
  setActiveCompany: (id: string | null) => void

  // Fetch methods
  fetchCompanies: () => Promise<void>
  fetchDashboardStats: () => Promise<void>
  fetchAgents: (companyId: string) => Promise<void>
  fetchTasks: (companyId: string) => Promise<void>
  fetchBudgetSummary: (companyId: string) => Promise<void>
  fetchBudgetEntries: (companyId: string) => Promise<void>
  fetchAuditLogs: (companyId: string, severity?: string) => Promise<void>
  fetchActivityFeed: (companyId: string) => Promise<void>

  // Convenience: load everything for a company
  loadCompanyData: (companyId: string) => Promise<void>

  // Trigger heartbeat
  triggerHeartbeat: () => Promise<void>
  createCompany: (data: any) => Promise<void>
  createTask: (data: any) => Promise<void>
}

export const usePhantomStore = create<PhantomStore>((set, get) => ({
  // ── Initial State ──────────────────────────────────────────────────
  activeCompanyId: null,
  companies: [],
  dashboardStats: null,
  agents: [],
  tasks: [],
  budgetSummary: null,
  budgetEntries: [],
  auditLogs: [],
  activityFeed: [],

  loading: {
    companies: false,
    stats: false,
    agents: false,
    tasks: false,
    budget: false,
    audit: false,
    activity: false,
  },

  error: null,

  // ── Actions ────────────────────────────────────────────────────────

  setActiveCompany: (id) => {
    set({ activeCompanyId: id })
    if (id) {
      get().loadCompanyData(id)
    }
  },

  fetchCompanies: async () => {
    set((s) => ({ loading: { ...s.loading, companies: true }, error: null }))
    try {
      const res = await api.get<CompanyResponse[]>('/companies')
      set((s) => ({
        companies: res.data,
        loading: { ...s.loading, companies: false },
      }))
      // Auto-select first company if none selected
      if (!get().activeCompanyId && res.data.length > 0) {
        get().setActiveCompany(res.data[0].id)
      }
    } catch (err: any) {
      set((s) => ({
        loading: { ...s.loading, companies: false },
        error: err.message,
      }))
    }
  },

  fetchDashboardStats: async () => {
    set((s) => ({ loading: { ...s.loading, stats: true } }))
    try {
      const res = await api.get<CompanyDashboardStats>('/companies/stats')
      set((s) => ({
        dashboardStats: res.data,
        loading: { ...s.loading, stats: false },
      }))
    } catch (err: any) {
      set((s) => ({ loading: { ...s.loading, stats: false }, error: err.message }))
    }
  },

  fetchAgents: async (companyId) => {
    set((s) => ({ loading: { ...s.loading, agents: true } }))
    try {
      const res = await api.get<AgentResponse[]>(`/agents/company/${companyId}`)
      set((s) => ({
        agents: res.data,
        loading: { ...s.loading, agents: false },
      }))
    } catch (err: any) {
      set((s) => ({ loading: { ...s.loading, agents: false }, error: err.message }))
    }
  },

  fetchTasks: async (companyId) => {
    set((s) => ({ loading: { ...s.loading, tasks: true } }))
    try {
      const res = await api.get<TaskResponse[]>(`/tasks/company/${companyId}`)
      set((s) => ({
        tasks: res.data,
        loading: { ...s.loading, tasks: false },
      }))
    } catch (err: any) {
      set((s) => ({ loading: { ...s.loading, tasks: false }, error: err.message }))
    }
  },

  fetchBudgetSummary: async (companyId) => {
    set((s) => ({ loading: { ...s.loading, budget: true } }))
    try {
      const res = await api.get<BudgetSummary>(`/budget/${companyId}/summary`)
      set((s) => ({
        budgetSummary: res.data,
        loading: { ...s.loading, budget: false },
      }))
    } catch (err: any) {
      set((s) => ({ loading: { ...s.loading, budget: false }, error: err.message }))
    }
  },

  fetchBudgetEntries: async (companyId) => {
    try {
      const res = await api.get<BudgetEntryResponse[]>(`/budget/${companyId}/entries`)
      set({ budgetEntries: res.data })
    } catch {
      // silent
    }
  },

  fetchAuditLogs: async (companyId, severity) => {
    set((s) => ({ loading: { ...s.loading, audit: true } }))
    try {
      const params: Record<string, string> = {}
      if (severity && severity !== 'all') params.severity = severity
      const res = await api.get<AuditEntry[]>(`/dashboard/audit/${companyId}`, { params })
      set((s) => ({
        auditLogs: res.data,
        loading: { ...s.loading, audit: false },
      }))
    } catch (err: any) {
      set((s) => ({ loading: { ...s.loading, audit: false }, error: err.message }))
    }
  },

  fetchActivityFeed: async (companyId) => {
    set((s) => ({ loading: { ...s.loading, activity: true } }))
    try {
      const res = await api.get<AuditEntry[]>(`/dashboard/activity/${companyId}`, {
        params: { limit: 10 },
      })
      set((s) => ({
        activityFeed: res.data,
        loading: { ...s.loading, activity: false },
      }))
    } catch (err: any) {
      set((s) => ({ loading: { ...s.loading, activity: false }, error: err.message }))
    }
  },

  loadCompanyData: async (companyId) => {
    const store = get()
    await Promise.allSettled([
      store.fetchDashboardStats(),
      store.fetchAgents(companyId),
      store.fetchTasks(companyId),
      store.fetchBudgetSummary(companyId),
      store.fetchBudgetEntries(companyId),
      store.fetchActivityFeed(companyId),
    ])
  },

  triggerHeartbeat: async () => {
    try {
      await api.post('/dashboard/heartbeat/trigger')
      // Refresh everything after heartbeat
      const companyId = get().activeCompanyId
      if (companyId) {
        get().loadCompanyData(companyId)
      }
    } catch (err: any) {
      set({ error: err.message })
    }
  },

  createCompany: async (data) => {
    try {
      const res = await api.post('/companies', data)
      await get().fetchCompanies()
      get().setActiveCompany(res.data.id)
    } catch (err: any) {
      set({ error: err.message })
      throw err
    }
  },

  createTask: async (data) => {
    try {
      await api.post('/tasks', data)
      const companyId = get().activeCompanyId
      if (companyId) {
        await get().fetchTasks(companyId)
        await get().fetchDashboardStats()
      }
    } catch (err: any) {
      set({ error: err.message })
      throw err
    }
  },
}))

import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const CompanyAPI = {
  getStats: () => api.get('/dashboard/stats'),
  listCompanies: () => api.get('/companies'),
  getCompany: (id: string) => api.get(`/companies/${id}`),
}

export const AgentAPI = {
  listAgents: (companyId: string) => api.get(`/agents/company/${companyId}`),
  getAgent: (id: string) => api.get(`/agents/${id}`),
}

export const TaskAPI = {
  listTasks: (companyId: string) => api.get(`/tasks/company/${companyId}`),
  updateTask: (id: string, data: any) => api.patch(`/tasks/${id}`, data),
}

export const BudgetAPI = {
  getSummary: (companyId: string) => api.get(`/budget/${companyId}/summary`),
  listEntries: (companyId: string) => api.get(`/budget/${companyId}/entries`),
}

export const AuditAPI = {
  getActivity: (companyId: string) => api.get(`/dashboard/activity/${companyId}`),
}

export default api

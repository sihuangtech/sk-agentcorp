import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ShellProvider, useShell } from './context/ShellContext'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { OverviewPage } from './pages/OverviewPage'
import { OrgChartPage } from './pages/OrgChartPage'
import { KanbanPage } from './pages/KanbanPage'
import { BudgetPage } from './pages/BudgetPage'
import { AuditPage } from './pages/AuditPage'
import { useWebSocket } from './hooks/useWebSocket'
import { usePhantomStore } from './lib/store'

import { SettingsPage } from './pages/SettingsPage'

const AppContent: React.FC = () => {
  const { isSidebarOpen, toggleSidebar } = useShell()
  const { fetchCompanies } = usePhantomStore()

  // Connect to WebSocket feed
  useWebSocket()

  // Fetch initial company data
  useEffect(() => {
    fetchCompanies()
  }, [fetchCompanies])

  return (
    <Router>
      <div className="flex bg-brand-bg min-h-screen text-slate-100 selection:bg-amber-500 selection:text-slate-900">
        <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />

        <main className={`flex-1 transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
          <Header />

          <div className="max-w-[1800px] mx-auto pb-24">
            <Routes>
              <Route path="/" element={<OverviewPage />} />
              <Route path="/org" element={<OrgChartPage />} />
              <Route path="/tasks" element={<KanbanPage />} />
              <Route path="/budget" element={<BudgetPage />} />
              <Route path="/audit" element={<AuditPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

function App() {
  return (
    <ShellProvider>
      <AppContent />
    </ShellProvider>
  )
}

export default App

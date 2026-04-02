import React, { useState, useEffect } from 'react'
import {
  Bell,
  Search,
  RefreshCcw,
  Zap,
  ChevronDown,
} from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { usePhantomStore } from '../../lib/store'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const Header: React.FC = () => {
  const [scrolled, setScrolled] = useState(false)
  const [companyDropdownOpen, setCompanyDropdownOpen] = useState(false)

  const {
    companies,
    activeCompanyId,
    setActiveCompany,
    dashboardStats,
    triggerHeartbeat,
    fetchCompanies,
  } = usePhantomStore()

  const activeCompany = companies.find((c) => c.id === activeCompanyId)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    fetchCompanies()
  }, [fetchCompanies])

  return (
    <header
      className={cn(
        'sticky top-0 right-0 z-40 h-20 transition-all duration-300 px-10 flex items-center justify-between',
        scrolled
          ? 'bg-brand-bg/90 backdrop-blur-3xl border-b border-white/5'
          : 'bg-transparent'
      )}
    >
      {/* SEARCH */}
      <div className="flex items-center gap-4 w-96 relative group">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-hover:text-amber-500 transition-colors" />
        <input
          type="text"
          placeholder="Search agents, tasks, or logs..."
          className="w-full h-11 bg-white/5 border border-white/5 rounded-2xl pl-12 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all focus:bg-white/10"
        />
        <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-1.5 px-2 py-1 rounded bg-white/5 border border-white/10">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">
            ⌘
          </span>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">
            K
          </span>
        </div>
      </div>

      {/* INDICATORS */}
      <div className="flex items-center gap-8">
        {/* COMPANY SELECTOR */}
        <div className="flex items-center gap-4 px-6 border-x border-white/5 relative">
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-none mb-1">
              Company Status
            </span>
            <button
              onClick={() => setCompanyDropdownOpen(!companyDropdownOpen)}
              className="flex items-center gap-1.5 hover:text-amber-400 transition-colors"
            >
              <div className="relative w-2 h-2 rounded-full bg-amber-500 shadow-lg shadow-amber-500/30">
                <span className="absolute inset-0 rounded-full bg-amber-500 animate-ping opacity-75" />
              </div>
              <span className="text-xs font-bold text-white tracking-wide">
                {activeCompany
                  ? `${activeCompany.is_paused ? 'PAUSED' : 'ACTIVE'}: ${activeCompany.name}`
                  : companies.length === 0
                    ? 'No Companies'
                    : 'Select Company'}
              </span>
              {companies.length > 1 && (
                <ChevronDown className="w-3 h-3 text-slate-500" />
              )}
            </button>
          </div>

          {/* Company Dropdown */}
          {companyDropdownOpen && (
            <div className="absolute top-full right-0 mt-2 w-64 bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl py-2 z-50">
              {companies.map((c) => (
                <button
                  key={c.id}
                  onClick={() => {
                    setActiveCompany(c.id)
                    setCompanyDropdownOpen(false)
                  }}
                  className={cn(
                    'w-full px-4 py-3 text-left hover:bg-white/5 transition-colors flex items-center gap-3',
                    c.id === activeCompanyId && 'bg-amber-500/10'
                  )}
                >
                  <div
                    className={cn(
                      'w-2 h-2 rounded-full',
                      c.is_active && !c.is_paused
                        ? 'bg-emerald-500'
                        : c.is_paused
                          ? 'bg-amber-500'
                          : 'bg-slate-500'
                    )}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-white truncate">
                      {c.name}
                    </p>
                    <p className="text-[10px] text-slate-500">
                      {c.agent_count} agents • {c.active_task_count} tasks
                    </p>
                  </div>
                </button>
              ))}
              
              <div className="border-t border-white/5 mt-2 pt-2 px-2">
                 <button
                  onClick={() => {
                    setCompanyDropdownOpen(false)
                    // Create minimal mockup company via store
                    usePhantomStore.getState().createCompany({
                      name: `New Virtual Corp ${Math.floor(Math.random() * 1000)}`,
                      template_id: 'saas_dev_agency'
                    })
                  }}
                  className="w-full px-4 py-2 bg-amber-500/10 text-amber-500 rounded-xl text-sm font-black uppercase tracking-widest hover:bg-amber-500/20 transition-colors"
                 >
                   + Create Company
                 </button>
              </div>
            </div>
          )}

          <button
            onClick={triggerHeartbeat}
            className="p-2 hover:bg-white/5 rounded-xl transition-colors hover:text-amber-500 group"
            title="Trigger heartbeat"
          >
            <RefreshCcw className="w-4 h-4 group-active:animate-spin" />
          </button>
        </div>

        {/* NOTIFICATIONS */}
        <div className="flex items-center gap-4">
          <div className="relative p-2.5 hover:bg-white/5 rounded-2xl cursor-pointer">
            <Bell className="w-5 h-5 text-slate-400" />
            {dashboardStats && dashboardStats.failed_tasks > 0 && (
              <span className="absolute top-1.5 right-1.5 w-3.5 h-3.5 bg-linear-to-br from-red-500 to-rose-700 border-2 border-brand-bg rounded-full flex items-center justify-center">
                <span className="text-[8px] font-bold text-white">
                  {dashboardStats.failed_tasks}
                </span>
              </span>
            )}
          </div>

          <div className="h-10 w-[1px] bg-white/10 mx-2" />

          {/* USER */}
          <div className="flex items-center gap-4 pl-4 group cursor-pointer">
            <div className="flex flex-col items-end">
              <span className="text-sm font-bold text-white group-hover:text-amber-400 transition-colors">
                Admin CEO
              </span>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">
                System Owner
              </span>
            </div>
            <div className="relative p-0.5 rounded-2xl bg-linear-to-br from-amber-200 to-amber-600 transition-transform group-hover:scale-105 active:scale-95">
              <img
                src="https://api.dicebear.com/7.x/pixel-art/svg?seed=SKAgentCorp&backgroundColor=0f172a"
                alt="User Avatar"
                className="w-12 h-12 rounded-[14px] bg-slate-900 border-2 border-slate-900/50"
              />
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-linear-to-br from-blue-500 to-indigo-700 rounded-full border-2 border-slate-900 flex items-center justify-center p-0.5 shadow-lg">
                <Zap className="w-2.5 h-2.5 text-white" fill="currentColor" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

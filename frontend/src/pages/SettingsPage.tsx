import React, { useState } from 'react'
import {
  Server,
  Key,
  ShieldAlert,
  Wallet,
  Cpu,
  Clock,
  Save,
  CheckCircle2,
  Database
} from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: any[]) {
  return twMerge(clsx(inputs))
}

export const SettingsPage: React.FC = () => {
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="px-10 py-6 space-y-8 animate-fade-in">
      <div>
        <h1 className="text-4xl font-bold tracking-tight premium-gradient-text uppercase">
          System Configuration
        </h1>
        <p className="text-slate-400 font-medium mt-1">
          Global OS engine parameters &bull; API Keys &bull; LLM Routing
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* API KEYS SECTION */}
        <div className="xl:col-span-2 space-y-6">
          <div className="glass-card p-8 rounded-3xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 bg-blue-500/10 rounded-xl text-blue-500">
                <Key className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">
                LLM Providers
              </h2>
            </div>
            
            <div className="space-y-4">
              {[
                { id: 'openai', name: 'OpenAI API Key', placeholder: 'sk-proj-...' },
                { id: 'anthropic', name: 'Anthropic API Key', placeholder: 'sk-ant-...' },
                { id: 'gemini', name: 'Google Gemini API Key', placeholder: 'AIza...' },
                { id: 'groq', name: 'Groq API Key', placeholder: 'gsk_...' }
              ].map((provider) => (
                <div key={provider.id}>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">
                    {provider.name}
                  </label>
                  <input
                    type="password"
                    placeholder={provider.placeholder}
                    className="w-full h-12 bg-slate-900/50 border border-white/5 rounded-xl px-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-8 rounded-3xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 bg-amber-500/10 rounded-xl text-amber-500">
                <Cpu className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">
                Engine & Anti-Stuck Parameters
              </h2>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">
                  Heartbeat Interval (Seconds)
                </label>
                <div className="relative">
                  <Clock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="number"
                    defaultValue={60}
                    className="w-full h-12 bg-slate-900/50 border border-white/5 rounded-xl pl-11 pr-4 text-white focus:outline-none focus:border-amber-500/50 transition-all font-mono"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">
                  Task Timeout (Seconds)
                </label>
                <div className="relative">
                  <ShieldAlert className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="number"
                    defaultValue={300}
                    className="w-full h-12 bg-slate-900/50 border border-white/5 rounded-xl pl-11 pr-4 text-white focus:outline-none focus:border-amber-500/50 transition-all font-mono"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">
                  Max Retries Per Agent
                </label>
                <input
                  type="number"
                  defaultValue={3}
                  className="w-full h-12 bg-slate-900/50 border border-white/5 rounded-xl px-4 text-white focus:outline-none focus:border-amber-500/50 transition-all font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">
                  Database Type
                </label>
                <div className="relative">
                  <Database className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <select className="w-full h-12 bg-slate-900/50 border border-white/5 rounded-xl pl-11 pr-4 text-white focus:outline-none focus:border-amber-500/50 transition-all appearance-none cursor-pointer">
                    <option value="sqlite">SQLite (Local)</option>
                    <option value="postgres">PostgreSQL</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* SIDEBAR SETTINGS */}
        <div className="space-y-6">
          <div className="glass-card p-8 rounded-3xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 bg-emerald-500/10 rounded-xl text-emerald-500">
                <Wallet className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">
                Global Budget
              </h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">
                  Hard Cap (USD)
                </label>
                <input
                  type="number"
                  defaultValue={5000}
                  className="w-full h-12 bg-slate-900/50 border border-white/5 rounded-xl px-4 text-white focus:outline-none focus:border-amber-500/50 transition-all font-mono"
                />
                <p className="text-[10px] text-slate-500 mt-2 font-medium">
                  The system will automatically suspend ALL agents globally if this budget is reached.
                </p>
              </div>
            </div>
          </div>

          <div className="glass-card p-8 rounded-3xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 bg-purple-500/10 rounded-xl text-purple-500">
                <Server className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">
                System Info
              </h2>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-white/5">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-bold">OS Version</span>
                <span className="text-sm text-white font-mono">v1.2.0-rc</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-white/5">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-bold">Engine</span>
                <span className="text-sm text-amber-500 font-mono">LangGraph Checkpoint</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-bold">Environment</span>
                <span className="text-sm text-emerald-500 font-mono">Production</span>
              </div>
            </div>
          </div>

          {/* SAVE BUTTON */}
          <button 
            onClick={handleSave}
            className={cn(
              "w-full h-14 rounded-2xl flex items-center justify-center gap-2 font-black uppercase tracking-widest transition-all",
              saved 
                ? "bg-emerald-500 text-slate-900 border-none shadow-lg shadow-emerald-500/25"
                : "premium-button text-slate-900 border-none shadow-lg shadow-amber-500/25"
            )}
          >
            {saved ? (
              <>
                <CheckCircle2 className="w-5 h-5" />
                Settings Saved
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Apply Changes
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

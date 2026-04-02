import React, { useEffect, useState } from 'react'
import { Terminal, Shield, AlertTriangle, Loader2 } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { usePhantomStore } from '../lib/store'
import { formatDistanceToNow } from 'date-fns'

function cn(...inputs: any[]) {
  return twMerge(clsx(inputs))
}

const severityConfig: Record<string, { icon: any; color: string; bg: string }> = {
  success: { icon: Shield, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  info: { icon: Terminal, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  warning: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10' },
  error: { icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10' },
}

export const AuditPage: React.FC = () => {
  const { auditLogs, activeCompanyId, fetchAuditLogs, loading } = usePhantomStore()
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    if (activeCompanyId) {
      fetchAuditLogs(activeCompanyId, filter === 'all' ? undefined : filter)
    }
  }, [activeCompanyId, filter, fetchAuditLogs])

  return (
    <div className="px-10 py-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight premium-gradient-text uppercase">
            Audit Trail
          </h1>
          <p className="text-slate-400 font-medium mt-1">
            Immutable event log &bull; Full system transparency
          </p>
        </div>
        <div className="flex items-center gap-2">
          {['all', 'success', 'info', 'warning', 'error'].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={cn(
                'px-3 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-lg transition-colors',
                filter === s
                  ? 'bg-amber-500 text-slate-900'
                  : 'bg-white/5 text-slate-400 hover:bg-white/10'
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-card rounded-3xl overflow-hidden">
        {loading.audit ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
          </div>
        ) : auditLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500 gap-3">
            <Terminal className="w-10 h-10 text-slate-600" />
            <p className="text-sm font-medium">
              {filter === 'all'
                ? 'No audit logs yet — activity will appear as the system operates'
                : `No ${filter} events found`}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-white/[0.03]">
            {auditLogs.map((entry) => {
              const config =
                severityConfig[entry.severity] || severityConfig.info
              const Icon = config.icon
              return (
                <div
                  key={entry.id}
                  className="flex items-start gap-4 p-5 hover:bg-white/[0.02] transition-colors group"
                >
                  <div className={cn('p-2.5 rounded-xl shrink-0 mt-0.5', config.bg)}>
                    <Icon className={cn('w-4 h-4', config.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={cn(
                          'text-[10px] font-black uppercase tracking-[0.15em] px-2 py-0.5 rounded-full border',
                          config.bg,
                          config.color
                        )}
                      >
                        {entry.event_type}
                      </span>
                      <span className="text-[10px] text-slate-600 font-bold uppercase">
                        by {entry.actor_name}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-white group-hover:text-amber-100 transition-colors">
                      {entry.message}
                    </p>
                  </div>
                  <div className="shrink-0 text-right">
                    <span className="text-[11px] text-slate-500 font-medium">
                      {formatDistanceToNow(new Date(entry.created_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

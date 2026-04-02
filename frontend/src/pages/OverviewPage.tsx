import React, { useEffect } from 'react'
import {
  Users,
  SquareKanban,
  Wallet,
  Activity,
  TrendingUp,
  TrendingDown,
  Terminal,
  PlayCircle,
  Loader2,
} from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { usePhantomStore } from '../lib/store'
import { formatDistanceToNow } from 'date-fns'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ═══════════════════════════════════════════════════════════════════════
//  Stat Card Component
// ═══════════════════════════════════════════════════════════════════════

const StatCard: React.FC<{
  title: string
  value: string | number
  icon: any
  change?: string
  isPositive?: boolean
  loading?: boolean
}> = ({ title, value, icon: Icon, change, isPositive, loading }) => (
  <div className="glass-card p-6 rounded-3xl transition-transform hover:scale-[1.02] group">
    <div className="flex items-center justify-between mb-4">
      <div className="p-3 bg-white/5 rounded-2xl group-hover:bg-amber-500/10 group-hover:text-amber-500 transition-colors">
        <Icon className="w-5 h-5" />
      </div>
      {change && (
        <div
          className={cn(
            'flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-full',
            isPositive
              ? 'text-emerald-500 bg-emerald-500/10'
              : 'text-rose-500 bg-rose-500/10'
          )}
        >
          {isPositive ? (
            <TrendingUp className="w-3 h-3" />
          ) : (
            <TrendingDown className="w-3 h-3" />
          )}
          {change}
        </div>
      )}
    </div>
    <div className="space-y-1">
      <h3 className="text-slate-400 text-sm font-medium tracking-tight uppercase">
        {title}
      </h3>
      {loading ? (
        <Loader2 className="w-6 h-6 text-slate-500 animate-spin mt-1" />
      ) : (
        <p className="text-3xl font-bold text-white tracking-tighter">{value}</p>
      )}
    </div>
  </div>
)

// ═══════════════════════════════════════════════════════════════════════
//  DASHBOARD PAGE — Real API data
// ═══════════════════════════════════════════════════════════════════════

export const OverviewPage: React.FC = () => {
  const dashboardStats = usePhantomStore((s) => s.dashboardStats)
  const activityFeed = usePhantomStore((s) => s.activityFeed)
  const loading = usePhantomStore((s) => s.loading)
  const triggerHeartbeat = usePhantomStore((s) => s.triggerHeartbeat)
  const fetchDashboardStats = usePhantomStore((s) => s.fetchDashboardStats)
  const fetchCompanies = usePhantomStore((s) => s.fetchCompanies)

  useEffect(() => {
    fetchDashboardStats()
    fetchCompanies()
  }, [fetchDashboardStats, fetchCompanies])

  const stats = dashboardStats
  const budgetUsed = stats ? stats.total_budget_spent : 0
  const budgetCap = stats ? stats.total_budget_cap : 1
  const budgetPct = budgetCap > 0 ? ((budgetUsed / budgetCap) * 100).toFixed(1) : '0'
  const reliability =
    stats && stats.total_tasks > 0
      ? (
          ((stats.completed_tasks) /
            (stats.completed_tasks + stats.failed_tasks || 1)) *
          100
        ).toFixed(1)
      : '100.0'

  // Build chart from company creation history (simple mock-free approach: show tasks by status)
  const chartData = stats
    ? [
        { name: 'Completed', val: stats.completed_tasks },
        { name: 'In Progress', val: stats.in_progress_tasks },
        { name: 'Failed', val: stats.failed_tasks },
        { name: 'Total', val: stats.total_tasks },
      ]
    : []

  return (
    <div className="space-y-8 animate-fade-in px-10 py-6">
      {/* WELCOME SECTION */}
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold tracking-tight text-white premium-gradient-text uppercase">
          System Command Center
        </h1>
        <p className="text-slate-400 font-medium">
          Monitoring{' '}
          <span className="text-amber-500 font-bold">
            {stats?.active_companies ?? 0} ACTIVE{' '}
            {(stats?.active_companies ?? 0) === 1 ? 'COMPANY' : 'COMPANIES'}
          </span>{' '}
          with{' '}
          <span className="text-amber-500 font-bold">
            {stats?.active_agents ?? 0} DEPLOYED AGENTS
          </span>
        </p>
      </div>

      {/* KEY STATS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Agents"
          value={stats?.active_agents ?? 0}
          icon={Users}
          change={stats ? `${stats.total_agents} total` : undefined}
          isPositive={true}
          loading={loading.stats}
        />
        <StatCard
          title="Tasks In Pipeline"
          value={stats?.in_progress_tasks ?? 0}
          icon={SquareKanban}
          change={stats ? `${stats.total_tasks} total` : undefined}
          isPositive={true}
          loading={loading.stats}
        />
        <StatCard
          title="Budget Utilization"
          value={`$${budgetUsed.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={Wallet}
          change={stats ? `${budgetPct}% of cap` : undefined}
          isPositive={Number(budgetPct) < 80}
          loading={loading.stats}
        />
        <StatCard
          title="Success Rate"
          value={`${reliability}%`}
          icon={Activity}
          change={
            stats
              ? `${stats.completed_tasks}/${stats.completed_tasks + stats.failed_tasks}`
              : undefined
          }
          isPositive={Number(reliability) > 90}
          loading={loading.stats}
        />
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* TASK STATUS CHART */}
        <div className="xl:col-span-2 glass-card p-8 rounded-3xl">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-xl font-bold tracking-tight text-white uppercase">
                Task Distribution
              </h2>
              <p className="text-sm text-slate-500 font-medium uppercase tracking-widest mt-1">
                Aggregate pipeline status
              </p>
            </div>
          </div>

          <div className="h-80 w-full">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="#1e293b"
                  />
                  <XAxis
                    dataKey="name"
                    stroke="#475569"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickMargin={10}
                  />
                  <YAxis
                    stroke="#475569"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickMargin={10}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#020617',
                      borderRadius: '16px',
                      border: '1px solid rgba(245,158,11,0.2)',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                    cursor={{ stroke: '#f59e0b', strokeWidth: 2 }}
                  />
                  <Area
                    type="monotone"
                    dataKey="val"
                    stroke="#f59e0b"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorValue)"
                    animationDuration={2000}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-sm">
                {loading.stats ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  'No data yet — create a company to start monitoring'
                )}
              </div>
            )}
          </div>
        </div>

        {/* REAL-TIME FEED */}
        <div className="glass-card p-8 rounded-3xl flex flex-col h-[500px]">
          <div className="flex items-center justify-between mb-8 shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-500/10 rounded-xl text-amber-500">
                <Terminal className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold tracking-tight text-white uppercase">
                Live Signals
              </h2>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-6 pr-2 scrollbar-none">
            {loading.activity ? (
              <div className="flex items-center justify-center h-32">
                <Loader2 className="w-6 h-6 text-slate-500 animate-spin" />
              </div>
            ) : activityFeed.length === 0 ? (
              <div className="flex items-center justify-center h-32 text-sm text-slate-500">
                No activity yet
              </div>
            ) : (
              activityFeed.map((item) => (
                <div key={item.id} className="flex gap-4 relative group cursor-default">
                  <div className="shrink-0 relative z-10">
                    <div
                      className={cn(
                        'w-10 h-10 rounded-2xl flex items-center justify-center border-2 border-brand-bg',
                        item.severity === 'success'
                          ? 'bg-emerald-500/20 text-emerald-500'
                          : item.severity === 'warning'
                            ? 'bg-amber-500/20 text-amber-500'
                            : item.severity === 'error'
                              ? 'bg-red-500/20 text-red-500'
                              : 'bg-blue-500/20 text-blue-500'
                      )}
                    >
                      <Terminal className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 pb-4">
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
                      {formatDistanceToNow(new Date(item.created_at), {
                        addSuffix: true,
                      })}
                    </span>
                    <p className="text-sm font-bold text-slate-100 leading-tight group-hover:text-white transition-colors">
                      {item.message}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="mt-6 pt-6 border-t border-white/5 shrink-0">
            <button
              onClick={triggerHeartbeat}
              className="w-full premium-button h-12 rounded-2xl flex items-center justify-center gap-2 text-slate-900 font-black uppercase tracking-widest text-xs"
            >
              <PlayCircle className="w-5 h-5" />
              Manually Trigger Heartbeat
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

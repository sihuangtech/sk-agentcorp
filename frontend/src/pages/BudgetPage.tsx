import React, { useEffect } from 'react'
import {
  Wallet,
  DollarSign,
  CreditCard,
  Receipt,
  Loader2,
} from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { usePhantomStore } from '../lib/store'
import { formatDistanceToNow } from 'date-fns'

function cn(...inputs: any[]) {
  return twMerge(clsx(inputs))
}

const PIE_COLORS = ['#f59e0b', '#3b82f6', '#10b981', '#6366f1', '#ec4899', '#8b5cf6']

export const BudgetPage: React.FC = () => {
  const {
    budgetSummary,
    budgetEntries,
    activeCompanyId,
    fetchBudgetSummary,
    fetchBudgetEntries,
    loading,
  } = usePhantomStore()

  useEffect(() => {
    if (activeCompanyId) {
      fetchBudgetSummary(activeCompanyId)
      fetchBudgetEntries(activeCompanyId)
    }
  }, [activeCompanyId, fetchBudgetSummary, fetchBudgetEntries])

  const summary = budgetSummary
  const cap = summary?.budget_cap_usd ?? 0
  const spent = summary?.total_spent_usd ?? 0
  const remaining = summary?.remaining_usd ?? 0
  const pct = summary?.utilization_pct ?? 0
  const avgCost =
    summary && summary.entries_count > 0
      ? (spent / summary.entries_count).toFixed(2)
      : '0.00'

  // Build pie data from cost_by_type
  const pieData = summary
    ? Object.entries(summary.cost_by_type).map(([name, value]) => ({
        name,
        value,
      }))
    : []

  // Daily spend bar chart
  const dailyData = summary?.daily_spend ?? []

  return (
    <div className="px-10 py-6 space-y-8 animate-fade-in">
      <div>
        <h1 className="text-4xl font-bold tracking-tight premium-gradient-text uppercase">
          Financial Ledger
        </h1>
        <p className="text-slate-400 font-medium mt-1">
          Real-time cost tracking &bull; Per-agent spend analytics
        </p>
      </div>

      {loading.budget ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
        </div>
      ) : !summary ? (
        <div className="glass-card rounded-3xl p-12 text-center text-slate-500">
          <Wallet className="w-12 h-12 mx-auto mb-4 text-slate-600" />
          <p className="font-medium">No budget data — create a company to start tracking costs</p>
        </div>
      ) : (
        <>
          {/* Top Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                title: 'Total Budget',
                value: `$${cap.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
                icon: Wallet,
                sub: 'Monthly cap',
                color: 'text-amber-500',
              },
              {
                title: 'Total Spent',
                value: `$${spent.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
                icon: CreditCard,
                sub: `${pct.toFixed(1)}% utilized`,
                color: 'text-blue-400',
              },
              {
                title: 'Remaining',
                value: `$${remaining.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
                icon: DollarSign,
                sub: summary.is_over_budget ? '⚠ Over budget!' : 'Available funds',
                color: summary.is_over_budget ? 'text-red-400' : 'text-emerald-400',
              },
              {
                title: 'Avg Cost/Entry',
                value: `$${avgCost}`,
                icon: Receipt,
                sub: `Across ${summary.entries_count} entries`,
                color: 'text-purple-400',
              },
            ].map((s) => (
              <div key={s.title} className="glass-card p-6 rounded-3xl">
                <div className="flex items-center gap-3 mb-3">
                  <div className={cn('p-2.5 rounded-xl bg-white/5', s.color)}>
                    <s.icon className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-sm text-slate-500 font-medium uppercase tracking-tight">
                  {s.title}
                </p>
                <p className="text-3xl font-bold text-white tracking-tighter mt-1">
                  {s.value}
                </p>
                <p className="text-[10px] text-slate-500 font-bold uppercase mt-2">
                  {s.sub}
                </p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Daily Spend Bar Chart */}
            <div className="xl:col-span-2 glass-card p-8 rounded-3xl">
              <h2 className="text-xl font-bold text-white uppercase tracking-tight mb-6">
                Daily Spend
              </h2>
              <div className="h-72">
                {dailyData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dailyData}>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        stroke="#1e293b"
                      />
                      <XAxis
                        dataKey="date"
                        stroke="#475569"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                      />
                      <YAxis
                        stroke="#475569"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(v) => `$${v}`}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#020617',
                          borderRadius: '16px',
                          border: '1px solid rgba(245,158,11,0.2)',
                          color: '#fff',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="amount" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-500 text-sm">
                    No daily spend data yet
                  </div>
                )}
              </div>
            </div>

            {/* Spend by Category Pie */}
            <div className="glass-card p-8 rounded-3xl">
              <h2 className="text-xl font-bold text-white uppercase tracking-tight mb-6">
                By Category
              </h2>
              {pieData.length > 0 ? (
                <>
                  <div className="h-52">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={4}
                          dataKey="value"
                        >
                          {pieData.map((_entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={PIE_COLORS[index % PIE_COLORS.length]}
                            />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#020617',
                            borderRadius: '12px',
                            border: '1px solid rgba(255,255,255,0.1)',
                            color: '#fff',
                            fontSize: '12px',
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-2 mt-4">
                    {pieData.map((c, i) => (
                      <div key={c.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2.5 h-2.5 rounded-full"
                            style={{
                              backgroundColor: PIE_COLORS[i % PIE_COLORS.length],
                            }}
                          />
                          <span className="text-xs font-medium text-slate-400">
                            {c.name}
                          </span>
                        </div>
                        <span className="text-xs font-bold text-white">
                          ${c.value.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center h-52 text-slate-500 text-sm">
                  No cost breakdown available
                </div>
              )}
            </div>
          </div>

          {/* Recent Entries Table */}
          <div className="glass-card rounded-3xl overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">
                Recent Transactions
              </h2>
            </div>
            {budgetEntries.length === 0 ? (
              <div className="p-12 text-center text-slate-500 text-sm">
                No transactions recorded yet
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] border-b border-white/5">
                      <th className="text-left p-4">Description</th>
                      <th className="text-left p-4">Model</th>
                      <th className="text-left p-4">Tokens (In/Out)</th>
                      <th className="text-right p-4">Cost</th>
                      <th className="text-right p-4">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {budgetEntries.map((e) => (
                      <tr
                        key={e.id}
                        className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
                      >
                        <td className="p-4 text-sm font-medium text-white">
                          {e.description || e.entry_type}
                        </td>
                        <td className="p-4 text-sm text-slate-400">
                          {e.llm_model || e.llm_provider || '—'}
                        </td>
                        <td className="p-4 text-xs text-slate-500 font-mono">
                          {e.tokens_input.toLocaleString()} /{' '}
                          {e.tokens_output.toLocaleString()}
                        </td>
                        <td className="p-4 text-sm font-bold text-amber-500 text-right">
                          ${e.amount_usd.toFixed(4)}
                        </td>
                        <td className="p-4 text-xs text-slate-500 text-right">
                          {formatDistanceToNow(new Date(e.created_at), {
                            addSuffix: true,
                          })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

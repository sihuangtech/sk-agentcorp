import React, { useEffect, useState } from 'react'
import {
  AlertTriangle,
  Play,
  MoreHorizontal,
  Loader2,
  SquareKanban,
} from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { usePhantomStore } from '../lib/store'
import type { TaskResponse } from '../lib/types'
import { formatDistanceToNow } from 'date-fns'

function cn(...inputs: any[]) {
  return twMerge(clsx(inputs))
}

const COLUMNS = [
  { id: 'queued', title: 'Queued', color: 'text-slate-400' },
  { id: 'in_progress', title: 'In Progress', color: 'text-blue-400' },
  { id: 'validating', title: 'Validating', color: 'text-amber-400' },
  { id: 'done', title: 'Completed', color: 'text-emerald-400' },
]

const priorityStyles: Record<string, string> = {
  critical: 'bg-red-500/10 text-red-400 border-red-500/20',
  high: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  medium: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  low: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
}

const TaskCard: React.FC<{ task: TaskResponse }> = ({ task }) => (
  <div className="glass-card p-4 rounded-2xl hover:border-amber-500/20 transition-all cursor-pointer group">
    <div className="flex items-start justify-between mb-3">
      <span
        className={cn(
          'text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border',
          priorityStyles[task.priority] || priorityStyles.medium
        )}
      >
        {task.priority}
      </span>
      <button className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white/5 rounded-lg">
        <MoreHorizontal className="w-4 h-4 text-slate-500" />
      </button>
    </div>
    <h4 className="text-sm font-bold text-white leading-snug mb-3">
      {task.title}
    </h4>
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 text-[10px] font-black">
          {task.assigned_agent_name
            ? task.assigned_agent_name
                .split(' ')
                .map((n) => n[0])
                .join('')
            : '??'}
        </div>
        <span className="text-[11px] text-slate-500 font-medium truncate max-w-[120px]">
          {task.assigned_agent_name || 'Unassigned'}
        </span>
      </div>
      {task.retry_count > 0 && (
        <div className="flex items-center gap-1 text-amber-500">
          <AlertTriangle className="w-3 h-3" />
          <span className="text-[10px] font-bold">
            {task.retry_count}/{task.max_retries}
          </span>
        </div>
      )}
    </div>
    {task.started_at && (
      <div className="mt-2 pt-2 border-t border-white/5">
        <span className="text-[10px] text-slate-600">
          Started{' '}
          {formatDistanceToNow(new Date(task.started_at), { addSuffix: true })}
        </span>
      </div>
    )}
  </div>
)

export const KanbanPage: React.FC = () => {
  const { tasks, activeCompanyId, fetchTasks, loading } = usePhantomStore()

  useEffect(() => {
    if (activeCompanyId) fetchTasks(activeCompanyId)
  }, [activeCompanyId, fetchTasks])

  // Group tasks into kanban columns by their kanban_column or status
  const groupedTasks: Record<string, TaskResponse[]> = {
    queued: [],
    in_progress: [],
    validating: [],
    done: [],
  }

  tasks.forEach((t) => {
    const col = t.kanban_column || t.status
    if (col in groupedTasks) {
      groupedTasks[col].push(t)
    } else if (col === 'completed') {
      groupedTasks.done.push(t)
    } else {
      groupedTasks.queued.push(t)
    }
  })

  // Sort each column by kanban_order
  Object.values(groupedTasks).forEach((arr) =>
    arr.sort((a, b) => a.kanban_order - b.kanban_order)
  )

  const [newTaskTitle, setNewTaskTitle] = useState('')

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim() || !activeCompanyId) return
    await usePhantomStore.getState().createTask({
      company_id: activeCompanyId,
      title: newTaskTitle,
      priority: 'medium',
      category: 'general',
    })
    setNewTaskTitle('')
  }

  return (
    <div className="px-10 py-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight premium-gradient-text uppercase">
            Task Pipeline
          </h1>
          <p className="text-slate-400 font-medium mt-1">
            Autonomous task lifecycle &bull; Anti-stuck protected
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input 
            type="text" 
            placeholder="Quick task title..." 
            value={newTaskTitle}
            onChange={e => setNewTaskTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreateTask()}
            className="px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm focus:outline-none focus:border-amber-500/50 w-64 text-white"
          />
          <button 
            onClick={handleCreateTask}
            className="premium-button px-5 py-2.5 rounded-xl text-sm font-black text-slate-900 uppercase tracking-wide flex items-center gap-2"
          >
            <Play className="w-4 h-4" /> Deploy Task
          </button>
        </div>
      </div>

      {loading.tasks ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-6 min-h-[calc(100vh-250px)]">
          {COLUMNS.map((col) => (
            <div key={col.id} className="flex flex-col">
              <div className="flex items-center justify-between mb-4 px-1">
                <div className="flex items-center gap-2.5">
                  <div
                    className={cn(
                      'w-2.5 h-2.5 rounded-full',
                      col.id === 'queued'
                        ? 'bg-slate-500'
                        : col.id === 'in_progress'
                          ? 'bg-blue-500'
                          : col.id === 'validating'
                            ? 'bg-amber-500'
                            : 'bg-emerald-500'
                    )}
                  />
                  <h3
                    className={cn(
                      'text-sm font-black uppercase tracking-widest',
                      col.color
                    )}
                  >
                    {col.title}
                  </h3>
                </div>
                <span className="text-xs font-bold text-slate-600 bg-white/5 px-2 py-0.5 rounded-full">
                  {groupedTasks[col.id]?.length || 0}
                </span>
              </div>
              <div className="flex-1 space-y-3 p-2 rounded-2xl bg-white/[0.02] border border-white/[0.03]">
                {groupedTasks[col.id]?.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-32 text-slate-600 gap-2">
                    <SquareKanban className="w-6 h-6" />
                    <span className="text-[10px] font-bold uppercase tracking-widest">
                      Empty
                    </span>
                  </div>
                ) : (
                  groupedTasks[col.id]?.map((task) => (
                    <TaskCard key={task.id} task={task} />
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

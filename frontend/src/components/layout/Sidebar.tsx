import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  SquareKanban, 
  Wallet, 
  History, 
  Settings, 
  Zap, 
  ChevronLeft, 
  ChevronRight,
  PlusCircle,
  Building2,
  Command
} from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const Sidebar: React.FC<{ isOpen: boolean; onToggle: () => void }> = ({ isOpen, onToggle }) => {
  const menuItems = [
    { name: 'Overview', icon: LayoutDashboard, path: '/' },
    { name: 'Org Chart', icon: Users, path: '/org' },
    { name: 'Kanban', icon: SquareKanban, path: '/tasks' },
    { name: 'Budget', icon: Wallet, path: '/budget' },
    { name: 'Audit Logs', icon: History, path: '/audit' },
  ]

  return (
    <aside className={cn(
      "fixed top-0 left-0 h-screen transition-all duration-300 z-50",
      "bg-brand-bg/80 backdrop-blur-2xl border-r border-white/5",
      isOpen ? "w-64" : "w-20"
    )}>
      {/* BRAND HEADER */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-white/5 mb-8">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-linear-to-br from-amber-400 to-amber-600 flex items-center justify-center shrink-0 shadow-lg shadow-amber-500/20">
            <Command className="w-5 h-5 text-slate-900" />
          </div>
          <h1 className={cn(
            "font-bold text-xl tracking-tight transition-opacity duration-200",
            isOpen ? "opacity-100" : "opacity-0 invisible"
          )}>
            Phantom<span className="text-amber-500">OS</span>
          </h1>
        </div>
        <button onClick={onToggle} className="p-1 hover:bg-white/5 rounded-md text-slate-400">
          {isOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
        </button>
      </div>

      {/* NAV ITEMS */}
      <nav className="px-4 space-y-2 mb-12">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 p-3 rounded-xl transition-all duration-300 group",
              isActive 
                ? "bg-amber-500/10 text-amber-500 shadow-inner" 
                : "text-slate-400 hover:text-white hover:bg-white/5"
            )}
          >
            <item.icon className={cn(
              "w-5 h-5 transition-transform group-hover:scale-110",
              isOpen ? "" : "mx-auto"
            )} />
            {isOpen && <span className="font-medium">{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* SYSTEM CONTROLS / SETTINGS */}
      <div className="px-4 mt-auto border-t border-white/5 pt-8 absolute bottom-8 w-full left-0">
        <NavLink
            to="/settings"
            className={({ isActive }) => cn(
              "flex items-center gap-3 p-3 rounded-xl mx-4",
              isActive ? "bg-amber-500/10 text-amber-500" : "text-slate-400 hover:text-white hover:bg-white/5"
            )}
          >
            <Settings className="w-5 h-5" />
            {isOpen && <span className="font-medium">System Settings</span>}
        </NavLink>
        
        {isOpen && (
            <div className="mx-4 mt-6 p-4 rounded-2xl bg-linear-to-br from-amber-500/5 to-transparent border border-amber-500/10">
                <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-4 h-4 text-amber-500 animate-pulse" />
                    <span className="text-xs font-bold text-amber-500 tracking-widest uppercase">System Core</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 w-3/4 animate-shimmer" />
                </div>
                <div className="flex justify-between mt-2">
                    <span className="text-[10px] text-slate-500 font-medium">Uptime: 24/7/365</span>
                    <span className="text-[10px] text-amber-500 font-bold uppercase">Optimized</span>
                </div>
            </div>
        )}
      </div>
    </aside>
  )
}

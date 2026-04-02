import React, { createContext, useContext, useState, ReactNode } from 'react'

interface ShellState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  activeCompanyId: string | null;
  setActiveCompanyId: (id: string | null) => void;
}

const ShellContext = createContext<ShellState | undefined>(undefined)

export const ShellProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [activeCompanyId, setActiveCompanyId] = useState<string | null>(null)

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)

  return (
    <ShellContext.Provider value={{ isSidebarOpen, toggleSidebar, activeCompanyId, setActiveCompanyId }}>
      {children}
    </ShellContext.Provider>
  )
}

export const useShell = () => {
  const context = useContext(ShellContext)
  if (!context) throw new Error('useShell must be used within ShellProvider')
  return context
}

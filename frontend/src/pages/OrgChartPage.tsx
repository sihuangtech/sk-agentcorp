import React, { useEffect, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
  Handle,
  Position,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Users, Zap, Target, Loader2 } from 'lucide-react'
import { usePhantomStore } from '../lib/store'
import type { AgentResponse } from '../lib/types'

const statusColors: Record<string, { dot: string; text: string }> = {
  idle: { dot: 'bg-emerald-500', text: 'text-emerald-500' },
  working: { dot: 'bg-blue-500', text: 'text-blue-500' },
  stuck: { dot: 'bg-red-500', text: 'text-red-500' },
  offline: { dot: 'bg-slate-500', text: 'text-slate-500' },
}

const AgentNode = ({ data }: { data: AgentResponse & { label: string } }) => {
  const sc = statusColors[data.status] || statusColors.idle
  return (
    <div className="px-5 py-4 shadow-2xl bg-slate-900/90 backdrop-blur-xl border border-amber-500/20 rounded-2xl min-w-[220px]">
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-amber-500 !w-2.5 !h-2.5"
      />
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-500 shrink-0">
          <Users className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <div className="text-[10px] font-black text-amber-500 uppercase tracking-[0.15em]">
            {data.title || data.role_id}
          </div>
          <div className="text-sm font-bold text-white leading-tight truncate">
            {data.name}
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-white/5 pt-2.5">
        <div className="flex items-center gap-1.5">
          <Zap className="w-3 h-3 text-amber-500" />
          <span className="text-[10px] font-bold text-slate-500 uppercase">
            {data.llm_model}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${sc.dot} animate-pulse`} />
          <span className={`text-[10px] font-bold uppercase ${sc.text}`}>
            {data.status}
          </span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-amber-500 !w-2.5 !h-2.5"
      />
    </div>
  )
}

const nodeTypes = { agent: AgentNode }

const defaultEdgeOptions = {
  style: { stroke: '#f59e0b', strokeWidth: 2, strokeOpacity: 0.3 },
  type: 'smoothstep' as const,
}

export const OrgChartPage: React.FC = () => {
  const { agents, activeCompanyId, fetchAgents, loading } = usePhantomStore()

  useEffect(() => {
    if (activeCompanyId) fetchAgents(activeCompanyId)
  }, [activeCompanyId, fetchAgents])

  // Build graph from agents and their reports_to relationships
  const { initialNodes, initialEdges } = useMemo(() => {
    if (agents.length === 0) return { initialNodes: [], initialEdges: [] }

    // Build lookup
    const byId = new Map(agents.map((a) => [a.id, a]))
    const byRole = new Map(agents.map((a) => [a.role_id, a]))

    // Layout: group by depth
    const roots = agents.filter((a) => !a.reports_to)
    const children = agents.filter((a) => a.reports_to)

    // Position agents in a tree layout
    const nodesArr = agents.map((agent) => {
      // Use stored position if available, otherwise auto-layout
      const isRoot = !agent.reports_to
      const rootIdx = roots.indexOf(agent)
      const childIdx = children.indexOf(agent)

      let x = agent.position_x
      let y = agent.position_y

      if (x === 0 && y === 0) {
        if (isRoot) {
          x = rootIdx * 300
          y = 0
        } else {
          // Find parent index to position under it
          const parent = agents.find(
            (a) => a.id === agent.reports_to || a.role_id === agent.reports_to
          )
          const parentRootIdx = parent ? roots.indexOf(parent) : 0
          x = parentRootIdx * 300 + childIdx * 260 - children.length * 50
          y = 200
        }
      }

      return {
        id: agent.id,
        type: 'agent' as const,
        position: { x, y },
        data: { ...agent, label: agent.name },
      }
    })

    const edgesArr = agents
      .filter((a) => a.reports_to)
      .map((a) => {
        // reports_to can be an agent_id or a role_id
        const parent =
          byId.get(a.reports_to!) || byRole.get(a.reports_to!)
        if (!parent) return null
        return {
          id: `e-${parent.id}-${a.id}`,
          source: parent.id,
          target: a.id,
          animated: parent.status === 'working',
        }
      })
      .filter(Boolean) as any[]

    return { initialNodes: nodesArr, initialEdges: edgesArr }
  }, [agents])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  // Update nodes when initialNodes change
  useEffect(() => {
    setNodes(initialNodes)
  }, [initialNodes, setNodes])

  useEffect(() => {
    setEdges(initialEdges)
  }, [initialEdges, setEdges])

  return (
    <div className="px-10 py-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-4xl font-bold tracking-tight premium-gradient-text uppercase">
          Organization Chart
        </h1>
        <p className="text-slate-400 font-medium mt-1">
          AI workforce hierarchy &bull; Drag nodes to rearrange
        </p>
      </div>

      <div className="h-[calc(100vh-250px)] w-full glass-card rounded-3xl overflow-hidden border border-white/5">
        {loading.agents ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
          </div>
        ) : agents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-3">
            <Users className="w-12 h-12 text-slate-600" />
            <p className="text-sm font-medium">
              No agents deployed yet — create a company to get started
            </p>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            fitView
            fitViewOptions={{ padding: 0.3 }}
          >
            <Background color="#1e293b" gap={24} size={1} />
            <Controls className="!bg-slate-900 !border-white/10 !rounded-xl !shadow-2xl [&>button]:!bg-slate-800 [&>button]:!border-white/5 [&>button]:!text-white [&>button:hover]:!bg-slate-700" />
            <MiniMap
              className="!bg-slate-900/80 !border-white/10 !rounded-xl"
              nodeColor="#f59e0b"
              maskColor="rgba(2, 6, 23, 0.7)"
            />
            <Panel position="top-left" className="!m-4">
              <div className="bg-slate-900/90 backdrop-blur-xl p-4 rounded-2xl border border-white/5 shadow-2xl">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-amber-500/10 rounded-xl">
                    <Target className="w-5 h-5 text-amber-500" />
                  </div>
                  <div>
                    <h3 className="text-sm font-black text-white uppercase tracking-widest">
                      Org Intelligence
                    </h3>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wide">
                      {agents.length} Autonomous Agents Deployed
                    </p>
                  </div>
                </div>
              </div>
            </Panel>
          </ReactFlow>
        )}
      </div>
    </div>
  )
}

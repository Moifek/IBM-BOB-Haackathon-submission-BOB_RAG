"use client"

import { useEffect, useState, useMemo } from "react"
import ReactFlow, { Background, Controls, Node, Edge, MarkerType } from "react-flow-renderer"

type GraphData = {
  nodes: Array<{ id: string; label: string; group?: string }>
  edges: Array<{ from: string; to: string }>
}

export function CodebaseGraph() {
  const [graph, setGraph] = useState<GraphData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/codebase")
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(setGraph)
      .catch(e => setError(String(e)))
  }, [])

  const { nodes, edges } = useMemo<{ nodes: Node[], edges: Edge[] }>(() => {
    if (!graph) return { nodes: [], edges: [] }

    // simple circular layout
    const radius = 140
    const cx = 250, cy = 150
    const nodes: Node[] = graph.nodes.map((n, i) => {
      const angle = (i / graph.nodes.length) * 2 * Math.PI
      return {
        id: n.id,
        data: { label: n.label },
        position: { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) },
        style: {
          background: "#1a1a1a",
          color: "#fff",
          border: "1px solid #6366f1",
          borderRadius: 8,
          fontSize: 11,
          padding: 6,
        },
      }
    })

    const edges: Edge[] = graph.edges.map((e, i) => ({
      id: `e${i}`,
      source: e.from,
      target: e.to,
      animated: true,
      style: { stroke: "#6366f1", strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
    }))

    return { nodes, edges }
  }, [graph])

  if (error) {
    return (
      <div className="text-sm text-muted-foreground">
        Run codebase analysis via <code className="bg-muted px-1 rounded">/api/codebase</code> to populate graph.
      </div>
    )
  }
  if (!graph) {
    return <div className="text-muted-foreground text-sm">Analyzing codebase...</div>
  }

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        proOptions={{ hideAttribution: true }}
        nodesDraggable={false}
      >
        <Background color="#222" gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}

"use client"

import { useEffect, useState } from "react"
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid,
} from "recharts"

type Trace = {
  id: string
  timestamp: string
  retrieval_ms: number
  generation_ms: number
  total_ms: number
}

export function RagTraces() {
  const [traces, setTraces] = useState<Trace[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function fetchTraces() {
      try {
        const res = await fetch("/api/traces")
        if (!res.ok) throw new Error(res.statusText)
        const data = await res.json()
        if (!cancelled) setTraces(data)
      } catch (e) {
        if (!cancelled) setError(String(e))
      }
    }
    fetchTraces()
    const interval = setInterval(fetchTraces, 5000)
    return () => { cancelled = true; clearInterval(interval) }
  }, [])

  if (error && !traces.length) {
    return (
      <div className="text-sm text-muted-foreground">
        Run a query (<code className="bg-muted px-1 rounded">bobrag query "..."</code>) to populate traces.
      </div>
    )
  }

  const chartData = traces.map((t, i) => ({
    n: i + 1,
    retrieval: t.retrieval_ms,
    generation: t.generation_ms,
    total: t.total_ms,
  }))

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#222" />
          <XAxis dataKey="n" stroke="#888" label={{ value: "Query #", position: "insideBottom", offset: -5, fill: "#888" }} />
          <YAxis stroke="#888" label={{ value: "ms", angle: -90, position: "insideLeft", fill: "#888" }} />
          <Tooltip
            contentStyle={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }}
          />
          <Legend />
          <Line type="monotone" dataKey="retrieval" stroke="#3b82f6" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="generation" stroke="#10b981" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="total" stroke="#6366f1" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

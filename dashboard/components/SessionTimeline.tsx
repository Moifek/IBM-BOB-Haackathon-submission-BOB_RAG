"use client"

import { useEffect, useState } from "react"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts"

type Session = {
  id: number
  name: string
  mode: string
  bobcoins: number
  files_read: string
  files_written: string
}

const MODE_COLORS: Record<string, string> = {
  "Ask": "#3b82f6",                  // blue
  "Plan": "#8b5cf6",                 // violet
  "Code": "#10b981",                 // emerald
  "docrag-auditor": "#6366f1",       // indigo (IBM-ish)
  "/review": "#f59e0b",              // amber
  "/create-pr": "#ec4899",           // pink
}

export function SessionTimeline() {
  const [data, setData] = useState<Session[]>([])

  useEffect(() => {
    fetch("/data/bob_sessions.json")
      .then(r => r.json())
      .then(setData)
      .catch(() => setData([]))
  }, [])

  if (!data.length) {
    return <div className="text-muted-foreground text-sm">Loading session data...</div>
  }

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
          <XAxis
            dataKey="id"
            stroke="#888"
            label={{ value: "Session #", position: "insideBottom", offset: -5, fill: "#888" }}
          />
          <YAxis
            stroke="#888"
            label={{ value: "Bobcoins", angle: -90, position: "insideLeft", fill: "#888" }}
          />
          <Tooltip
            contentStyle={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }}
            labelStyle={{ color: "#fff" }}
            formatter={(value: number, _name, props) => [
              `${value} Bobcoins · ${props.payload.mode}`,
              props.payload.name,
            ]}
          />
          <Bar dataKey="bobcoins" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={MODE_COLORS[entry.mode] ?? "#888"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-3 mt-3 text-xs text-muted-foreground">
        {Object.entries(MODE_COLORS).map(([mode, color]) => (
          <div key={mode} className="flex items-center gap-1.5">
            <span
              className="inline-block w-3 h-3 rounded-sm"
              style={{ background: color }}
            />
            {mode}
          </div>
        ))}
      </div>
    </div>
  )
}

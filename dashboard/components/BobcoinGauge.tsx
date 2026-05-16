"use client"

import { useEffect, useState } from "react"
import {
  RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis,
} from "recharts"

const BUDGET = 40

export function BobcoinGauge() {
  const [spent, setSpent] = useState<number>(0)

  useEffect(() => {
    fetch("/data/bob_sessions.json")
      .then(r => r.json())
      .then((sessions: Array<{ bobcoins: number }>) => {
        setSpent(sessions.reduce((sum, s) => sum + (s.bobcoins ?? 0), 0))
      })
      .catch(() => setSpent(0))
  }, [])

  const pct = (spent / BUDGET) * 100
  const color =
    spent < BUDGET * 0.625 ? "#10b981" :     // green <25
    spent < BUDGET * 0.875 ? "#f59e0b" :     // amber 25-35
    "#ef4444"                                 // red >35

  const data = [{ name: "spent", value: spent, fill: color }]

  return (
    <div className="relative" style={{ width: "100%", height: 240 }}>
      <ResponsiveContainer>
        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          data={data}
          startAngle={90}
          endAngle={-270}
        >
          <PolarAngleAxis type="number" domain={[0, BUDGET]} tick={false} />
          <RadialBar
            dataKey="value"
            cornerRadius={8}
            background={{ fill: "#1f1f1f" }}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <div className="text-4xl font-bold" style={{ color }}>{spent}</div>
        <div className="text-sm text-muted-foreground">/ {BUDGET} Bobcoins</div>
        <div className="text-xs text-muted-foreground mt-1">{pct.toFixed(0)}% used</div>
      </div>
    </div>
  )
}

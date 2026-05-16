"use client"

import { useEffect, useState } from "react"
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip,
} from "recharts"

type EvalResult = {
  faithfulness: number
  answer_relevancy: number
  context_precision: number
  context_recall: number
}

export function RagasRadar() {
  const [result, setResult] = useState<EvalResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/eval")
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(setResult)
      .catch(e => setError(String(e)))
  }, [])

  if (error) {
    return (
      <div className="text-sm text-muted-foreground">
        Run <code className="bg-muted px-1 rounded">bobrag eval</code> to populate this chart.
      </div>
    )
  }

  if (!result) {
    return <div className="text-muted-foreground text-sm">Loading evaluation...</div>
  }

  const data = [
    { metric: "Faithfulness", value: result.faithfulness, full: 1 },
    { metric: "Answer Relevancy", value: result.answer_relevancy, full: 1 },
    { metric: "Context Precision", value: result.context_precision, full: 1 },
    { metric: "Context Recall", value: result.context_recall, full: 1 },
  ]

  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <RadarChart data={data}>
          <PolarGrid stroke="#333" />
          <PolarAngleAxis dataKey="metric" stroke="#aaa" fontSize={11} />
          <PolarRadiusAxis angle={90} domain={[0, 1]} stroke="#555" tick={{ fontSize: 10 }} />
          <Radar
            name="BobRAG-MD"
            dataKey="value"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.4}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }}
            formatter={(v: number) => v.toFixed(3)}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

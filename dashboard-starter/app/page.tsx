import { SessionTimeline } from "@/components/SessionTimeline"
import { BobcoinGauge } from "@/components/BobcoinGauge"
import { RagTraces } from "@/components/RagTraces"
import { RagasRadar } from "@/components/RagasRadar"
import { CodebaseGraph } from "@/components/CodebaseGraph"

function Card({ title, subtitle, children, span = 1 }: {
  title: string; subtitle?: string; children: React.ReactNode; span?: number
}) {
  return (
    <div
      className={`bg-card rounded-2xl border border-border p-6 ${
        span === 2 ? "lg:col-span-2" : ""
      }`}
    >
      <div className="mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}

export default function Page() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <header className="mb-10 flex items-end justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-baseline gap-3">
              <h1 className="text-4xl font-bold tracking-tight">
                Bob<span className="text-primary">alytics</span>
              </h1>
              <span className="text-sm text-muted-foreground">
                BobRAG-MD · IBM Bob Hackathon · May 2026
              </span>
            </div>
            <p className="text-muted-foreground mt-2 max-w-2xl">
              Others built dashboards to monitor remote workers.
              I built one to monitor my AI worker — IBM Bob — building a medical RAG system, under tight token discipline.
            </p>
          </div>
          <div className="flex gap-3 text-xs">
            <a
              href="https://github.com/your-username/bobrag-md"
              className="text-muted-foreground hover:text-foreground underline underline-offset-2"
            >
              GitHub
            </a>
            <a
              href="/sessions"
              className="text-muted-foreground hover:text-foreground underline underline-offset-2"
            >
              Sessions
            </a>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card
            title="Bob Session Timeline"
            subtitle="Every session, by mode, by Bobcoin cost"
            span={2}
          >
            <SessionTimeline />
          </Card>

          <Card title="Bobcoin Budget" subtitle="Hard limit: 40">
            <BobcoinGauge />
          </Card>

          <Card title="RAG Query Traces" subtitle="Live from Langfuse">
            <RagTraces />
          </Card>

          <Card title="Ragas Evaluation" subtitle="Latest run">
            <RagasRadar />
          </Card>

          <Card title="Codebase Dependencies" subtitle="src/bobrag/ module graph">
            <CodebaseGraph />
          </Card>
        </div>

        <footer className="mt-12 pt-6 border-t border-border text-xs text-muted-foreground flex justify-between">
          <span>BobRAG-MD by Ahmed · MIT License</span>
          <span>Built solo in 36h with surgical Bob usage</span>
        </footer>
      </div>
    </main>
  )
}

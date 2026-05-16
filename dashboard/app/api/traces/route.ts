import { NextResponse } from "next/server"
import { Langfuse } from "langfuse"

const lf = new Langfuse({
  publicKey: process.env.LANGFUSE_PUBLIC_KEY!,
  secretKey: process.env.LANGFUSE_SECRET_KEY!,
  baseUrl: process.env.LANGFUSE_HOST ?? "https://cloud.langfuse.com",
})

export async function GET() {
  try {
    // Fetch via REST since SDK doesn't expose list directly
    const auth = Buffer
      .from(`${process.env.LANGFUSE_PUBLIC_KEY}:${process.env.LANGFUSE_SECRET_KEY}`)
      .toString("base64")
    const host = process.env.LANGFUSE_HOST ?? "https://cloud.langfuse.com"
    const res = await fetch(`${host}/api/public/traces?limit=10&orderBy=timestamp.desc`, {
      headers: { Authorization: `Basic ${auth}` },
      cache: "no-store",
    })
    if (!res.ok) throw new Error(`Langfuse API: ${res.status}`)
    const json = await res.json()

    const traces = (json.data ?? []).map((t: any) => ({
      id: t.id,
      timestamp: t.timestamp,
      retrieval_ms: t.observations?.find((o: any) => o.name?.includes("retriev"))?.latency ?? 0,
      generation_ms: t.observations?.find((o: any) => o.name?.includes("generat"))?.latency ?? 0,
      total_ms: t.latency ?? 0,
    })).reverse()

    return NextResponse.json(traces)
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 })
  }
}

import { NextResponse } from "next/server"
import { readFile } from "fs/promises"
import path from "path"

export async function GET() {
  try {
    const file = path.resolve(process.cwd(), "..", "eval", "results", "latest.json")
    const content = await readFile(file, "utf-8")
    const data = JSON.parse(content)
    // Expect aggregate keys
    return NextResponse.json({
      faithfulness: data.faithfulness ?? 0,
      answer_relevancy: data.answer_relevancy ?? 0,
      context_precision: data.context_precision ?? 0,
      context_recall: data.context_recall ?? 0,
    })
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 404 })
  }
}

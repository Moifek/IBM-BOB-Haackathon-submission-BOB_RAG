import { NextResponse } from "next/server"
import { exec } from "child_process"
import { promisify } from "util"
import path from "path"

const execAsync = promisify(exec)

/**
 * Scans `analysis-target/src/` (vendored DocRAG-MD source) with Python AST
 * and returns a dependency graph: nodes = files, edges = imports.
 *
 * Cross-platform: tries `python` first (Windows), falls back to `python3`.
 */
export async function GET() {
  try {
    const repoRoot = path.resolve(process.cwd(), "..").replace(/\\/g, "/")

    const py = `import ast, json; from pathlib import Path; root = Path("${repoRoot}/analysis-target/src"); files = [f for f in root.rglob("*.py") if "__pycache__" not in str(f) and f.stem != "__init__"]; mod_to_id = {f.stem: f.stem for f in files}; nodes = [{"id": fid, "label": fid + ".py"} for fid in mod_to_id.values()]; edges = []; [edges.append({"from": f.stem, "to": part}) for f in files for node in (ast.walk(ast.parse(f.read_text(errors='ignore'))) if f.exists() else []) if isinstance(node, ast.ImportFrom) and node.module for part in node.module.split(".") if part in mod_to_id and part != f.stem]; print(json.dumps({"nodes": nodes[:30], "edges": edges[:50]}))`

    let stdout: string
    try {
      const r = await execAsync(`python -c "${py.replace(/"/g, '\\"')}"`, {
        maxBuffer: 2 * 1024 * 1024,
      })
      stdout = r.stdout
    } catch {
      const r = await execAsync(`python3 -c "${py.replace(/"/g, '\\"')}"`, {
        maxBuffer: 2 * 1024 * 1024,
      })
      stdout = r.stdout
    }

    return NextResponse.json(JSON.parse(stdout.trim()))
  } catch (e) {
    return NextResponse.json(
      {
        error: String(e),
        hint: "Ensure Python is on PATH and analysis-target/src/ exists with .py files.",
      },
      { status: 500 },
    )
  }
}

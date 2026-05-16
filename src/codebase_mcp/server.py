"""MCP Server for DocRAG-MD Codebase Intelligence

Exposes the DocRAG-MD codebase as queryable tools for AI assistants.
Provides semantic search over functions, architecture explanations,
tech debt queries, and data flow tracing.

Usage:
    python -m src.codebase_mcp.server
    # Runs on http://localhost:9003/mcp
"""
import os
import json
from pathlib import Path
from typing import Literal
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("docrag_codebase")

# Load documentation artifacts
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"
CODE_MAP_PATH = DOCS_DIR / "CODE_MAP.md"
ARCHITECTURE_PATH = DOCS_DIR / "ARCHITECTURE.md"
TECH_DEBT_PATH = DOCS_DIR / "TECH_DEBT.md"
ONBOARDING_PATH = DOCS_DIR / "ONBOARDING.md"


def _load_doc(path: Path) -> str:
    """Load documentation file, return empty string if not found."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _parse_code_map() -> dict[str, list[dict]]:
    """Parse CODE_MAP.md into structured function catalog.
    
    Returns:
        Dict mapping file paths to list of function metadata dicts
    """
    content = _load_doc(CODE_MAP_PATH)
    if not content:
        return {}
    
    catalog = {}
    current_file = None
    
    for line in content.split("\n"):
        # Detect file headers like "## `retrieval/hybrid_retriever.py`"
        if line.startswith("## `") and line.endswith("`"):
            current_file = line.strip("## `").strip("`")
            catalog[current_file] = []
        
        # Parse function rows from markdown tables
        # Format: | `function_name` | Purpose | Params | Return |
        elif current_file and line.startswith("| `") and "Purpose" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3:
                func_name = parts[0].strip("`")
                purpose = parts[1]
                catalog[current_file].append({
                    "name": func_name,
                    "purpose": purpose,
                    "file": current_file
                })
    
    return catalog


def _parse_tech_debt() -> list[dict]:
    """Parse TECH_DEBT.md into structured findings list.
    
    Returns:
        List of tech debt finding dicts with severity, files, description
    """
    content = _load_doc(TECH_DEBT_PATH)
    if not content:
        return []
    
    findings = []
    current_finding = None
    
    for line in content.split("\n"):
        # Detect finding headers like "### 1. Title"
        if line.startswith("### ") and ". " in line:
            if current_finding:
                findings.append(current_finding)
            
            title = line.split(". ", 1)[1].strip()
            current_finding = {
                "title": title,
                "severity": "",
                "files": [],
                "description": ""
            }
        
        # Parse severity
        elif current_finding and line.startswith("**Severity:**"):
            if "High" in line:
                current_finding["severity"] = "High"
            elif "Medium" in line:
                current_finding["severity"] = "Medium"
            elif "Low" in line:
                current_finding["severity"] = "Low"
        
        # Parse files
        elif current_finding and line.startswith("**Files:**"):
            files_text = line.split("**Files:**")[1].strip()
            current_finding["files"] = [f.strip() for f in files_text.split(",")]
        
        # Accumulate description
        elif current_finding and line.strip() and not line.startswith("**"):
            current_finding["description"] += line.strip() + " "
    
    if current_finding:
        findings.append(current_finding)
    
    return findings


@mcp.tool()
def search_codebase(
    query: str,
    file_filter: str | None = None
) -> list[dict]:
    """Search the DocRAG-MD codebase for functions matching a query.
    
    Performs semantic search over the function catalog from CODE_MAP.md.
    Returns relevant functions with their purpose and location.
    
    Args:
        query: Natural language search query (e.g., "functions that do reranking")
        file_filter: Optional file path filter (e.g., "retrieval/")
    
    Returns:
        List of matching functions with name, purpose, file path
    
    Example:
        search_codebase("hybrid search functions")
        # Returns: [{"name": "hybrid_search", "purpose": "...", "file": "..."}]
    """
    catalog = _parse_code_map()
    if not catalog:
        return [{"error": "CODE_MAP.md not found or empty"}]
    
    # Simple keyword matching (could be enhanced with embeddings)
    query_lower = query.lower()
    results = []
    
    for file_path, functions in catalog.items():
        # Apply file filter if provided
        if file_filter and file_filter not in file_path:
            continue
        
        for func in functions:
            # Match query against function name or purpose
            if (query_lower in func["name"].lower() or 
                query_lower in func["purpose"].lower()):
                results.append(func)
    
    # Limit to top 10 results
    return results[:10]


@mcp.tool()
def explain_component(
    component: Literal[
        "orchestrator",
        "hybrid_retriever", 
        "crag",
        "rag_agent",
        "diagnosis_agent",
        "pharmacology_agent",
        "generator",
        "llm_router",
        "mcp_servers",
        "graphrag",
        "self_rag",
        "deep_search"
    ]
) -> dict:
    """Get detailed explanation of a DocRAG-MD component.
    
    Returns architecture overview, key technologies, and data flow
    for the specified component from ARCHITECTURE.md.
    
    Args:
        component: Component name (orchestrator, hybrid_retriever, etc.)
    
    Returns:
        Dict with component description, technologies, and flow
    
    Example:
        explain_component("hybrid_retriever")
        # Returns: {"description": "...", "technologies": [...], "flow": "..."}
    """
    arch_content = _load_doc(ARCHITECTURE_PATH)
    if not arch_content:
        return {"error": "ARCHITECTURE.md not found"}
    
    # Component-specific extraction logic
    component_map = {
        "orchestrator": "Orchestrator",
        "hybrid_retriever": "Hybrid Retriever",
        "crag": "CRAG",
        "rag_agent": "RAG Agent",
        "diagnosis_agent": "Diagnosis Agent",
        "pharmacology_agent": "Pharmacology Agent",
        "generator": "Generation",
        "llm_router": "LLM Router",
        "mcp_servers": "MCP Servers",
        "graphrag": "GraphRAG",
        "self_rag": "Self-RAG",
        "deep_search": "Deep Search"
    }
    
    search_term = component_map.get(component, component)
    
    # Extract relevant sections
    lines = arch_content.split("\n")
    description = []
    in_relevant_section = False
    
    for line in lines:
        if search_term.lower() in line.lower():
            in_relevant_section = True
        elif line.startswith("##") and in_relevant_section:
            break
        elif in_relevant_section and line.strip():
            description.append(line.strip())
    
    # Extract from Key Technologies table
    tech_section = []
    in_tech_table = False
    for line in lines:
        if "Key Technologies" in line:
            in_tech_table = True
        elif in_tech_table and line.startswith("|") and search_term in line:
            tech_section.append(line)
        elif in_tech_table and line.startswith("##"):
            break
    
    return {
        "component": component,
        "description": " ".join(description[:5]) if description else f"Component: {search_term}",
        "technologies": tech_section,
        "full_architecture": "See ARCHITECTURE.md for complete details"
    }


@mcp.tool()
def get_tech_debt(
    severity: Literal["High", "Medium", "Low", "All"] = "All",
    file_filter: str | None = None
) -> list[dict]:
    """Query technical debt findings from TECH_DEBT.md.
    
    Returns ranked tech debt items filtered by severity and/or file path.
    Each finding includes severity, affected files, description, and recommendations.
    
    Args:
        severity: Filter by severity level (High, Medium, Low, or All)
        file_filter: Optional file path filter (e.g., "agents/")
    
    Returns:
        List of tech debt findings matching filters
    
    Example:
        get_tech_debt(severity="High")
        # Returns: [{"title": "...", "severity": "High", "files": [...], ...}]
    """
    findings = _parse_tech_debt()
    if not findings:
        return [{"error": "TECH_DEBT.md not found or empty"}]
    
    # Apply filters
    filtered = []
    for finding in findings:
        # Severity filter
        if severity != "All" and finding["severity"] != severity:
            continue
        
        # File filter
        if file_filter:
            if not any(file_filter in f for f in finding["files"]):
                continue
        
        filtered.append(finding)
    
    return filtered


@mcp.tool()
def trace_data_flow(
    start: Literal[
        "user_query",
        "orchestrator",
        "agent",
        "retrieval",
        "generation"
    ],
    end: Literal[
        "orchestrator",
        "agent", 
        "retrieval",
        "generation",
        "response"
    ]
) -> dict:
    """Trace data flow through DocRAG-MD pipeline from start to end point.
    
    Returns step-by-step flow description extracted from ARCHITECTURE.md
    data flow section.
    
    Args:
        start: Starting point in pipeline
        end: Ending point in pipeline
    
    Returns:
        Dict with flow steps and component interactions
    
    Example:
        trace_data_flow(start="user_query", end="response")
        # Returns: {"steps": [...], "components": [...]}
    """
    arch_content = _load_doc(ARCHITECTURE_PATH)
    if not arch_content:
        return {"error": "ARCHITECTURE.md not found"}
    
    # Extract Data Flow section
    lines = arch_content.split("\n")
    flow_section = []
    in_flow = False
    
    for line in lines:
        if "## Data Flow" in line:
            in_flow = True
        elif in_flow and line.startswith("##"):
            break
        elif in_flow and line.strip():
            flow_section.append(line.strip())
    
    # Parse numbered steps
    steps = []
    for line in flow_section:
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.")):
            steps.append(line)
    
    # Filter steps based on start/end
    start_idx = 0
    end_idx = len(steps)
    
    start_keywords = {
        "user_query": ["User Input", "Query"],
        "orchestrator": ["Orchestrator", "Intent Classification"],
        "agent": ["Agent Routing", "Agent"],
        "retrieval": ["Retrieval", "Search", "HyDE"],
        "generation": ["Generation", "LLM Router"]
    }
    
    end_keywords = {
        "orchestrator": ["Orchestrator", "Intent Classification"],
        "agent": ["Agent Routing", "Agent"],
        "retrieval": ["Retrieval", "Search", "Rerank"],
        "generation": ["Generation", "LLM Router"],
        "response": ["Response", "Streamed"]
    }
    
    # Find start index
    for i, step in enumerate(steps):
        if any(kw in step for kw in start_keywords.get(start, [])):
            start_idx = i
            break
    
    # Find end index
    for i, step in enumerate(steps):
        if any(kw in step for kw in end_keywords.get(end, [])):
            end_idx = i + 1
            break
    
    relevant_steps = steps[start_idx:end_idx]
    
    return {
        "start": start,
        "end": end,
        "steps": relevant_steps,
        "step_count": len(relevant_steps),
        "full_flow": "See ARCHITECTURE.md Data Flow section for complete details"
    }


@mcp.tool()
def get_onboarding_task(
    task_number: Literal[1, 2, 3]
) -> dict:
    """Get a specific onboarding task from ONBOARDING.md.
    
    Returns detailed instructions for day-1 developer tasks.
    
    Args:
        task_number: Task number (1, 2, or 3)
    
    Returns:
        Dict with task goal, steps, and success criteria
    
    Example:
        get_onboarding_task(task_number=1)
        # Returns: {"goal": "...", "steps": [...], "success": "..."}
    """
    onboarding_content = _load_doc(ONBOARDING_PATH)
    if not onboarding_content:
        return {"error": "ONBOARDING.md not found"}
    
    # Extract task section
    lines = onboarding_content.split("\n")
    task_section = []
    in_task = False
    task_header = f"### Task {task_number}:"
    
    for line in lines:
        if line.startswith(task_header):
            in_task = True
        elif in_task and line.startswith("### Task"):
            break
        elif in_task and line.startswith("---"):
            break
        elif in_task:
            task_section.append(line)
    
    return {
        "task_number": task_number,
        "content": "\n".join(task_section),
        "full_guide": "See ONBOARDING.md for complete onboarding guide"
    }


if __name__ == "__main__":
    port = int(os.getenv("MCP_CODEBASE_PORT", "9003"))
    print(f"Starting DocRAG-MD Codebase MCP Server on port {port}")
    print(f"Docs directory: {DOCS_DIR}")
    print(f"Available tools: search_codebase, explain_component, get_tech_debt, trace_data_flow, get_onboarding_task")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")

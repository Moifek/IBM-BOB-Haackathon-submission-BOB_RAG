# BOB Framework - Multi-Agent Orchestration System

## Overview

The BOB Framework is a multi-agent orchestration system that coordinates specialized AI modes to execute software development tasks. Each mode has a specific role and set of capabilities, working together under the coordination of an Orchestrator to deliver complete features from planning through documentation.

## Agent Roster

### 🔀 Orchestrator Mode
**Role**: Team Lead & Workflow Coordinator

**Capabilities**:
- Creates and manages TODO lists for task tracking
- Delegates work to specialized modes
- Monitors progress and coordinates retries
- Manages context caching across mode switches
- Generates pull requests with auto-generated descriptions
- Integrates with Jira and GitHub for project management

### 💻 Code Mode
**Role**: Implementation Specialist

**Capabilities**:
- Writes and modifies code across all programming languages
- Creates new files and project structures
- Executes commands and runs tests
- Applies surgical edits to existing code
- Verifies implementations with linting and testing
- Reports file changes for cache invalidation

### ✅ Validator Mode (Plan Mode)
**Role**: Quality Assurance & Verification

**Capabilities**:
- Validates implementations against requirements
- Runs tests and checks for errors
- Reviews git diffs to verify changes
- Performs read-only inspections
- Provides diagnostic analysis for failed tasks
- Reports validation results with detailed findings

### 📝 Documenter Mode
**Role**: Documentation Specialist

**Capabilities**:
- Generates markdown documentation for features
- Creates technical implementation guides
- Documents APIs, functions, and configurations
- Integrates with Confluence for knowledge management
- Posts summaries to Jira tickets
- Uses cached context for efficient documentation

## Agentic Workflow

### Standard Execution Flow

```
User Request
    ↓
Orchestrator: Analyze & Create TODO List
    ↓
For Each Task:
    ├─→ Code Mode: Implement
    ├─→ Validator Mode: Verify
    └─→ Retry if needed (max 3 attempts)
    ↓
Orchestrator: Final Validation
    ↓
Orchestrator: Git Diff Review
    ↓
Orchestrator: Create Pull Request (optional)
    ↓
Documenter Mode: Generate Documentation
    ↓
Orchestrator: Report Completion
```

### Retry Protocol

When validation fails, the framework follows a 3-stage retry process:

1. **Attempt 1**: Initial implementation and validation
2. **Attempt 2**: Re-implementation with failure context
3. **Attempt 3**: Diagnostic analysis followed by corrective implementation

If all attempts fail, the task is marked as blocked and an incident report is generated.

## Key Features

### Context Caching
Reduces redundant file reads by maintaining a shared cache across mode switches. Files are cached during planning and invalidated when modified, improving performance and reducing token usage.

### Incremental Validation
Each task is validated immediately after implementation, catching issues early rather than discovering them at the end of the workflow.

### Bounded Execution
The retry protocol caps attempts at 3 per task, preventing unbounded token spend while providing intelligent escalation through diagnostic analysis.

### Safety Mechanisms
A pre-execution hook blocks destructive commands (rm -rf, git push --force, etc.) and requires explicit user approval, preventing accidental data loss.

### EARS Requirements Format
Uses Easy Approach to Requirements Syntax for clear, testable acceptance criteria with patterns like WHEN/SHALL, IF/THEN/SHALL, and WHILE/SHALL.

### GitHub Integration
Auto-generates pull request descriptions from git diffs and creates PRs with proper templates, streamlining the code review process.

### Jira Integration
Fetches ticket details, extracts requirements, and posts completion summaries directly to Jira issues through MCP tools.

### Git-Aware Validation
Validator mode uses git diff to verify changes match expectations, ensuring no unintended modifications were made.

### Careful Mode
Protects against destructive operations by intercepting dangerous commands and requiring user confirmation before execution.

### TODO-Based Planning
Uses simple TODO lists with status markers (pending, in-progress, complete) for transparent progress tracking throughout workflows.

## File Structure

```
.bob/
├── AGENTS.md                    # Global rules and conventions
├── custom_modes.yaml            # Custom mode definitions
├── modes/
│   └── documenter-prompt.md    # Documenter mode instructions
├── rules-orchestrator/
│   └── 01-team-lead.md         # Orchestrator workflow rules
├── rules-code/
│   └── 01-builder.md           # Code mode implementation rules
├── rules-validator/
│   └── 01-validator.md         # Validator verification rules
└── scripts/
    └── check-careful.sh        # Safety hook for destructive commands
```

## Mode Capabilities Matrix

| Capability | Orchestrator | Code | Validator | Documenter |
|-----------|-------------|------|-----------|------------|
| Read Files | ✅ | ✅ | ✅ | ✅ |
| Write Files | ✅ | ✅ | ❌ | ✅* |
| Execute Commands | ✅ | ✅ | ❌ | ❌ |
| Delegate Tasks | ✅ | ❌ | ❌ | ❌ |
| Manage TODO Lists | ✅ | ❌ | ❌ | ❌ |
| Git Operations | ✅ | ✅ | ✅ | ❌ |
| MCP Tools | ✅ | ❌ | ❌ | ✅** |

*Documenter can only write to `app_docs/` directory  
**Documenter uses Atlassian MCP tools only

## Communication Style

The framework follows these communication principles:

- **Concise and Direct**: Brief descriptions without unnecessary elaboration
- **Honest Assessment**: Clear statements about limitations and issues
- **Focused Execution**: Single-responsibility per mode, no scope creep
- **Explicit Reporting**: Clear status updates with specific details
- **Cache-Aware**: Transparent about file reads and cache utilization

## Documentation

- **Global Rules**: [`AGENTS.md`](AGENTS.md) - Communication style, EARS format, and careful mode
- **Mode Rules**: `rules-*/` directories - Detailed behavior specifications for each mode
- **Custom Modes**: [`custom_modes.yaml`](custom_modes.yaml) - Mode definitions and configurations

---

*Built for BOB (IBM's AI Assistant Platform)*
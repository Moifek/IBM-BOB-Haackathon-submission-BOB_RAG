---
inclusion: always
---

# AI Response Preferences

## Command Execution
- When asked to check/list a directory, use `ls -la` to give a full picture and let the user decide next steps
- Don't overcomplicate commands with unnecessary checks or chaining

## Core Communication Style
- Be concise and brief in all descriptions
- End messages with follow-up questions when clarification or next steps are needed
- Brutal honesty and realistic takes over vague "maybes" or "it might work"
- If something won't work well, say it directly
- If there are better alternatives, state them clearly
- Don't sugarcoat technical limitations or problems

## Formatting Rules
- No em dashes (avoid using — in responses)
- Keep explanations short and to the point
- Cut the fluff

## What This Means
- "This approach has serious performance issues and will likely fail at scale" instead of "This might have some performance considerations"
- "That won't work because X" instead of "That could potentially have some challenges"
- "Use Y instead, it's better for your use case" instead of "You might want to consider Y as an alternative"

---

## Modes Separation of Concerns
- orchestrator: owns EARS formatting, property extraction, plan parsing & task orchestrator, MCP tools
- documenter: prose docs only, mcp tools for documentation (Obsidian, Atlassian, ...)
- code: code execution only, no spec creation, no MCP tools
- validator: read-only verification, unchanged
- ask: conversational, exploration, up to date information, web_tools & MCP tools

# Careful Mode

Before running any destructive command, ask the user for explicit confirmation.

## Destructive Commands
- `rm -r` / `rm -rf` (except build artifacts: node_modules, .next, dist, __pycache__, .cache, build, .turbo, coverage)
- `DROP TABLE` / `DROP DATABASE`
- `TRUNCATE`
- `git push --force` / `git push -f`
- `git reset --hard`
- `git checkout .` / `git restore .`
- `docker rm -f` / `docker system prune`

## Behavior
- Never run these commands without asking first
- Explain what the command will destroy and why it's needed
- Suggest safer alternatives when possible (e.g., `git stash` instead of `git reset --hard`)
- The hook `~/.bob/scripts/check-careful.sh` enforces this as a hard block on `execute_bash`

---

# EARS - Easy Approach to Requirements Syntax

Reference for writing unambiguous, testable requirements and task specifications.

## EARS Patterns

### Event-Driven (WHEN/SHALL)
`WHEN <trigger>, THE <system> SHALL <response>`
Example: WHEN a user submits the login form, THE system SHALL validate credentials and return a JWT token.

### Conditional (IF/THEN/SHALL)
`IF <condition>, THEN THE <system> SHALL <response>`
Example: IF the session token is expired, THEN THE system SHALL redirect the user to the login page.

### State-Driven (WHILE/SHALL)
`WHILE <state>, THE <system> SHALL <behavior>`
Example: WHILE the application is in offline mode, THE system SHALL queue all write operations for later sync.

### Optional/Variant (WHERE/SHALL)
`WHERE <option/variant>, THE <system> SHALL <behavior>`
Example: WHERE the tenant has SMS notifications enabled, THE system SHALL send appointment reminders via SMS.

### Compound
Combine patterns: `WHILE <state>, WHEN <trigger>, IF <condition>, THEN THE <system> SHALL <response>`

## Conversion Rules

- Identify the trigger, condition, or state that activates the behavior
- Use SHALL for mandatory behavior (not "should", "may", "might")
- One behavior per criterion (split compound requirements)
- Make every criterion testable with clear pass/fail outcome
- Avoid vague terms - specify exact behaviors

## Property Extraction for Testing

### Round-Trip
*For any* X, applying operation then its inverse should return equivalent X.

### Invariant
*For any* X, after operation Y, property Z should still hold.

### Validation
*For any* invalid input X, operation should reject it.

### State Transition
*For any* state X, transition Y should result in valid state Z.

---
inclusion: always
version: 1.0
---

# Context Caching Strategy

## Purpose
Reduce redundant file reads across mode switches by maintaining a shared context cache. This improves performance and reduces token usage when multiple modes need to access the same files.

## Cache Structure

The cache is a conceptual shared memory space that persists across mode switches within a single workflow execution. Each mode can read from and write to the cache.

### Cache Entry Format
```
{
  "path": "relative/file/path",
  "content": "file contents",
  "hash": "content hash for validation",
  "timestamp": "last read/write time",
  "mode": "mode that last accessed"
}
```

## Caching Rules

### When to Cache (READ Operations)
1. **Always cache** when reading files that other modes will likely need:
   - Configuration files (package.json, tsconfig.json, etc.)
   - Core implementation files being worked on
   - Test files related to current task
   - Documentation being referenced

2. **Cache during task execution** when:
   - Orchestrator reads files for planning
   - Code mode reads files before modification
   - Validator reads files for verification
   - Documenter reads files for documentation

3. **Cache key files** that are frequently accessed:
   - Project manifests
   - Main entry points
   - Shared utilities
   - Type definitions

### When to Invalidate (WRITE Operations)
1. **Immediately invalidate** when:
   - Any mode writes to a file using `write_to_file`
   - Any mode modifies a file using `apply_diff`
   - Any mode inserts content using `insert_content`

2. **Invalidate related files** when:
   - A file is deleted or renamed
   - Dependencies change (package.json, requirements.txt)
   - Configuration files are modified

### When NOT to Cache
1. **Skip caching** for:
   - Very large files (>10,000 lines)
   - Binary files
   - Generated files (build artifacts)
   - Temporary files
   - Files in excluded directories (node_modules, .git, etc.)

## Implementation Protocol

### For Orchestrator Mode
When delegating tasks via `new_task`:
1. Include cache manifest in task message
2. List cached files with their paths
3. Specify which files are relevant to the task
4. Note any files that were recently modified (invalidated)

**Example delegation message:**
```
Task: Implement user authentication

Cached Context Available:
- src/app.ts (entry point, 150 lines)
- src/config/database.ts (DB config, 80 lines)
- package.json (dependencies)

Recently Modified (cache invalidated):
- src/routes/auth.ts (just created)

Please implement the authentication middleware.
```

### For Code Mode
1. **Before reading**: Check if file is in cache manifest from Orchestrator
2. **If cached**: Reference the cached content, no need to re-read
3. **If not cached**: Read file and note it for cache
4. **After writing**: Report which files were modified for cache invalidation

**Report format:**
```
Files Modified (invalidate cache):
- src/routes/auth.ts (created)
- src/app.ts (modified, added auth import)

Files Read (add to cache):
- src/middleware/logger.ts (referenced pattern)
```

### For Validator Mode
1. **Before reading**: Check cache manifest from Orchestrator
2. **Use cached content** when available
3. **Report cache hits**: Note which cached files were used
4. **No invalidation**: Validator is read-only

**Report format:**
```
Cache Utilization:
- src/routes/auth.ts (cache miss, read fresh)
- src/app.ts (cache hit, used cached version)
- package.json (cache hit)
```

### For Documenter Mode
1. **Before reading**: Check cache manifest from Orchestrator
2. **Use cached content** for implementation files
3. **Report cache usage**: Note which files were referenced
4. **Invalidate docs**: When writing to app_docs/

**Report format:**
```
Documentation Generated:
- app_docs/feature-auth.md (created, invalidate if cached)

Implementation Files Referenced (from cache):
- src/routes/auth.ts
- src/middleware/auth.ts
```

## Cache Lifecycle

### Workflow Start
1. Orchestrator initializes empty cache
2. Reads key files for planning
3. Populates initial cache

### During Execution
1. Orchestrator delegates with cache manifest
2. Code mode uses cache, reports modifications
3. Orchestrator updates cache (invalidates modified files)
4. Validator uses updated cache
5. Cycle repeats for each task

### Workflow End
1. Cache is discarded
2. No persistence between workflow executions
3. Fresh cache for next workflow

## Benefits

1. **Reduced Token Usage**: Avoid re-reading same files multiple times
2. **Faster Execution**: Less time spent on file I/O
3. **Consistency**: All modes work with same file versions
4. **Explicit Invalidation**: Clear tracking of what changed

## Cache Manifest Format

Orchestrator maintains and passes this structure:

```markdown
## Context Cache Manifest

### Cached Files
- `src/app.ts` (250 lines, hash: abc123, last: orchestrator)
- `package.json` (45 lines, hash: def456, last: orchestrator)
- `src/config/db.ts` (80 lines, hash: ghi789, last: code)

### Invalidated (Modified)
- `src/routes/auth.ts` (created by code mode)
- `src/app.ts` (modified by code mode, re-read required)

### Cache Statistics
- Total cached: 3 files
- Cache hits: 5
- Cache misses: 2
- Invalidations: 2
```

## Best Practices

1. **Be Explicit**: Always mention when using cached content
2. **Report Changes**: Always report file modifications for invalidation
3. **Validate Hashes**: If content seems stale, re-read and update cache
4. **Limit Cache Size**: Don't cache more than 20-30 files per workflow
5. **Prioritize**: Cache files most likely to be reused
6. **Clean Communication**: Include cache manifest in all mode delegations

## Error Handling

### Cache Miss
- If expected cached file is not available, read it fresh
- Report cache miss for Orchestrator to update manifest

### Stale Cache
- If cached content seems outdated, re-read file
- Report discrepancy for investigation

### Cache Corruption
- If cache entry is invalid, discard and re-read
- Continue execution, don't block on cache issues

## Monitoring

Track these metrics in workflow reports:
- Cache hit rate (hits / total reads)
- Files cached per workflow
- Invalidations per workflow
- Token savings estimate

## Example Workflow with Caching

```
1. Orchestrator reads src/app.ts, package.json (cache: 2 files)
2. Orchestrator delegates to Code mode with cache manifest
3. Code mode uses cached src/app.ts, modifies it (invalidate)
4. Code mode reports modification
5. Orchestrator updates cache (invalidate src/app.ts)
6. Orchestrator delegates to Validator with updated manifest
7. Validator re-reads src/app.ts (cache miss), uses cached package.json
8. Validator reports cache hit for package.json
9. Orchestrator delegates to Documenter with manifest
10. Documenter uses cached files for documentation
11. Workflow complete, cache discarded
```

This caching strategy reduces redundant reads while maintaining consistency through explicit invalidation on writes.
# BobRAG Testing Plan

## Test Checklist

### 1. Docker Compose Test
**Command:** `docker compose up`

**Expected:**
- Qdrant service starts successfully on port 6333
- Qdrant healthcheck passes
- bobrag service builds without errors
- No immediate crashes

**Verification:**
```bash
docker compose up -d
docker compose ps  # Both services should be "healthy" or "running"
curl http://localhost:6333/collections  # Should return JSON
```

### 2. Ingestion Test
**Command:** `uv run python -m bobrag ingest`

**Prerequisites:**
- Docker compose is running (Qdrant available)
- `.env` file exists with required keys
- `data/corpus/` contains at least one `.txt` file

**Expected:**
- Pipeline initializes without errors
- Qdrant collection created
- Documents chunked and embedded
- Chunks uploaded to Qdrant
- Success message printed

**Verification:**
```bash
# Check collection exists
curl http://localhost:6333/collections/bobrag_medical

# Check points count
curl http://localhost:6333/collections/bobrag_medical
# Should show points_count > 0
```

### 3. Query Test
**Command:** `uv run python -m bobrag query "What is metformin used for?"`

**Prerequisites:**
- Ingestion completed successfully
- Qdrant has indexed documents
- Gemini API key is valid

**Expected:**
- Query embeds successfully
- Qdrant search returns contexts
- Gemini generates answer with citations
- Answer printed to console with sources
- Langfuse trace created (if configured)

**Verification:**
- Answer contains medical information
- Answer cites sources like `[Source: metformin.txt]`
- Retrieved contexts shown with scores
- No errors in output

## Environment Requirements

Required `.env` variables:
```
GEMINI_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=bobrag_medical
LANGFUSE_PUBLIC_KEY=optional
LANGFUSE_SECRET_KEY=optional
LANGFUSE_HOST=http://localhost:3000
```

## Common Issues

### Issue: Qdrant connection refused
**Solution:** Ensure `docker compose up` is running and Qdrant is healthy

### Issue: No documents found
**Solution:** Check `data/corpus/` has `.txt` files

### Issue: Gemini API error
**Solution:** Verify `GEMINI_API_KEY` in `.env`

### Issue: Import errors
**Solution:** Run `uv sync` to install dependencies

## Next Steps After Tests Pass

1. Switch to code mode
2. Run actual tests
3. Fix any issues found
4. Update README with verified instructions
5. Mark test items as complete in todo list

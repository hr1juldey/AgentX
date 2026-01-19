# T007: Create Health Endpoint

**Phase**: 0
**Estimated Time**: 10 minutes
**Dependencies**: T006
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/incremental_release_plan.md` - Phase 0: Health endpoint

**Description**:
NOTE: Health endpoint was already created in T006. This task verifies the health endpoint is complete and adds extended health checks.

---

## Acceptance Criteria

**Passing Criteria**:
- Health endpoint responds at `/health`
- Returns JSON with status, app_name, version
- Returns 200 status code
- Works without authentication

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Start server (background)
python3 -m agentx.main &
SERVER_PID=$!
sleep 3

# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy","app_name":"AGENTX","version":"1.0.0"}

# Kill server
kill $SERVER_PID 2>/dev/null || true
```

---

## Implementation Steps

### Step 1: Verify health endpoint exists

Health endpoint is already in `agentx/main.py` from T006. Verify:

```python
# Check this code exists in main.py
@	/app.get("/health")
	async def health_check():
	"""Health check endpoint."""
	return {
		"status": "healthy",
		"app_name": get_settings().app_name,
		"version": get_settings().version,
	}
```

### Step 2: Add extended health check (optional)

Optionally add component health checks to main.py:

```python
@	@app.get("/health/extended")
	async def extended_health_check():
	"""Extended health check with component status."""
		from agentx.core.dependencies import (
			get_qdrant_adapter,
			get_ollama_adapter,
		)

		components = {}

		# Check Qdrant (will fail in Phase 0, that's OK)
		try:
			qdrant = get_qdrant_adapter()
			# TODO: Actual health check
			components["qdrant"] = {"status": "unknown"}
		except Exception as e:
			components["qdrant"] = {"status": "error", "error": str(e)}

		# Check Ollama
		try:
			ollama = get_ollama_adapter()
			# TODO: Actual health check
			components["ollama"] = {"status": "unknown"}
		except Exception as e:
			components["ollama"] = {"status": "error", "error": str(e)}

		return {
			"status": "healthy",
			"components": components,
		}
```

---

## Expected Failures & Countermeasures

### Failure: Port already in use

**Likelihood**: Low
**Symptoms**: `OSError: [Errno 48] Address already in use`

**Countermeasures**:
1. Kill process using port: `lsof -ti:8000 | xargs kill`
2. Or change port in .env: `PORT=8001`

**Recovery Time**: 2 minutes

### Failure: Server fails to start

**Likelihood**: Low
**Symptoms**: Import errors or configuration errors

**Countermeasures**:
1. Check all previous tasks (T001-T006) are complete
2. Verify all imports in main.py have corresponding modules
3. Run import test: `python3 -c "from agentx.main import create_app"`

**Recovery Time**: 10 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T006 main.py changed
**Detection**: Health endpoint missing or modified
**Action**: Re-run T006 or add health endpoint back

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Health endpoint path changes
**Prevention**: `/health` path is LOCKED
**Mitigation**: Update monitoring systems
**Affected Tasks**: All monitoring/alerting tasks

---

## Artifacts

**Files Modified**:
- `agentx/main.py` (Add extended health check, optional)

**Locked APIs**:
- `/health` endpoint path
- Health response JSON structure

---

## Quality Gates

**Quality Checks**:
- **Check**: Health endpoint accessible
  - Command: `curl -s http://localhost:8000/health | python3 -m json.tool`
  - Expected: JSON with status, app_name, version
  - Required: Yes

---

## Notes

1. Basic health endpoint created in T006 (this task is verification)
2. Extended health checks will work in Phase 1+ when adapters exist
3. Health endpoint should NOT require authentication
4. Used by monitoring systems and load balancers

---

## Completion Checklist

- [ ] Health endpoint exists in main.py
- [ ] Returns correct JSON structure
- [ ] Accessible at /health
- [ ] Returns 200 status code
- [ ] No authentication required
- [ ] Ready for T008 (Stub Repositories)

---

**Task T007 is part of Phase 0: Minimal System**
**Locked API**: /health endpoint path and response structure

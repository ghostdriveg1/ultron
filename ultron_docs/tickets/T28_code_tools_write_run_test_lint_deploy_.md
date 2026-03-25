# T28 — Code Tools (Write/Run/Test/Lint/Deploy)

## Context
Code tools: write (any language), run (Python/Node), test (pytest/jest), lint (pylint/eslint), fast-apply (deterministic edits), GitHub (commit/PR/deploy).

**Dependencies:** T27  
**Complexity:** HIGH

## Files to Create
(See Tech Plan directory structure for this component)

## Core Implementation
(See Core Flows document for this component's flow details)

## Acceptance Criteria
- [ ] Component works in isolation (unit tests pass)
- [ ] Component works with dependent components (integration tests pass)
- [ ] Performance meets spec (see Core Flows timing)
- [ ] Error cases handled gracefully
- [ ] Documented at function level
- [ ] No hardcoded secrets
- [ ] Entropy score monitored and reported

## Edge Cases
- Service unavailable: graceful degradation to fallback
- Unexpected input format: Pydantic validation catches it
- Timeout: circuit breaker prevents infinite wait

# T36 — AlphaEvolve Self-Modification Engine

## Context
AlphaEvolve evolutionary loop for self-modification: Generate 10 variants → Evaluate → Select top 3 → Crossover → Repeat → Canary deploy → Merge. Never degrades, always improves.

**Dependencies:** T35  
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

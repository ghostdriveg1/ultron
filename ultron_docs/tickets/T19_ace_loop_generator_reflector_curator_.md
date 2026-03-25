# T19 — ACE Loop (Generator/Reflector/Curator)

## Context
ACE loop: after every task, Generator did it, Reflector analyzes what worked/failed, Curator extracts reusable lessons. +10.6% benchmark improvement. Never makes same mistake twice.

**Dependencies:** T18  
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

# T31 — Computer Use (Agent S3 + Gemini Vision)

## Context
Computer use: Agent S3 (human-level, 72.6% OSWorld), Gemini Vision (screen understanding), UI-TARS-1.5-7B (pixel grounding), Xvfb (virtual display on ClawCloud Instance 3).

**Dependencies:** T30  
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

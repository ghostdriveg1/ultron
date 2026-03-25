# T30 — ChE Tools (Mass Balance/Thermo/VLE/NIST)

## Context
Ghost's competitive advantage: domain-specific ChE tools. Mass balance calculations, CoolProp thermodynamics, VLE, McCabe-Thiele diagrams, NIST chemistry data, PubChem properties, Pint unit conversion.

**Dependencies:** T29  
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

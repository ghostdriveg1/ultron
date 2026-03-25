---
name: Mass Balance
description: Solve steady-state and unsteady-state mass balance problems for chemical engineering processes
---

# Mass Balance Skill

## Trigger Patterns
- "solve mass balance"
- "calculate mass balance"
- "material balance"
- "conservation of mass"
- "feed and product streams"

## Steps
1. **Identify the system boundary** — Draw a control volume around the process unit(s)
2. **List all streams** — Feed streams (in), product streams (out), recycle streams
3. **Write the general equation** — Accumulation = In − Out + Generation − Consumption
4. **For steady-state** — Accumulation = 0, so: In + Generation = Out + Consumption
5. **For non-reactive** — Generation = Consumption = 0, so: In = Out
6. **Solve** — Use scipy.optimize or numpy for linear/nonlinear systems
7. **Verify** — Check that all component balances and overall balance close to within 0.1%

## Example
```
Feed: 100 kg/h, 40% A, 60% B
Product 1: ? kg/h, 90% A, 10% B
Product 2: ? kg/h, 10% A, 90% B

Overall: 100 = P1 + P2
Component A: 40 = 0.9*P1 + 0.1*P2
Solution: P1 = 37.5 kg/h, P2 = 62.5 kg/h
```

## Common Pitfalls
- Forgetting to account for recycle streams
- Mixing mass and molar units
- Not checking degree of freedom before solving
- Ignoring accumulation in batch processes

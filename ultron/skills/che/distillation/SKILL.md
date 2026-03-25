---
name: Distillation Column Design
description: Design binary distillation columns using McCabe-Thiele method and Fenske-Underwood-Gilliland
---

# Distillation Column Design Skill

## Trigger Patterns
- "design distillation column"
- "McCabe-Thiele"
- "number of stages"
- "reflux ratio"
- "VLE diagram"

## Steps
1. **Get VLE data** — Use CoolProp or Antoine equation for vapor pressures
2. **Calculate relative volatility** — α = P_A_sat / P_B_sat
3. **Determine feed condition** — q-line (subcooled, saturated, superheated)
4. **Minimum reflux** — Underwood equation or graphical from McCabe-Thiele
5. **Operating reflux** — Typically 1.2-1.5 × R_min
6. **Number of stages** — McCabe-Thiele graphical stepping or Fenske equation
7. **Feed stage** — Locate optimal feed stage from diagram
8. **Plot** — Generate xy-diagram with operating lines using matplotlib

## Example
```python
# Ethanol-water at 1 atm
# Feed: 50 mol% ethanol, saturated liquid
# Distillate: 90 mol% ethanol
# Bottoms: 10 mol% ethanol
# R = 1.5 * R_min
```

## Common Pitfalls
- Using weight fractions instead of mole fractions
- Ignoring azeotrope (ethanol-water at 89.4 mol%)
- Not accounting for Murphree tray efficiency
- Assuming constant molar overflow without verification

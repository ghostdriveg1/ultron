---
name: Thermodynamics
description: Solve thermodynamic problems using CoolProp and Pint for chemical engineering applications
---

# Thermodynamics Skill

## Trigger Patterns
- "calculate enthalpy"
- "find vapor pressure"
- "thermodynamic properties"
- "heat capacity"
- "Clausius-Clapeyron"
- "phase diagram"

## Steps
1. **Identify the substance** — Use CoolProp's fluid database (180+ fluids)
2. **Determine the state** — Temperature, pressure, or quality (vapor fraction)
3. **Look up properties** — Use CoolProp: `PropsSI('H', 'T', T, 'P', P, fluid)`
4. **Apply equations** — First/second law, energy balances, entropy calculations
5. **Unit conversion** — Use Pint for all unit conversions (never manual)
6. **Validate** — Cross-check with NIST WebBook data

## Example
```python
from CoolProp.CoolProp import PropsSI
import pint
ureg = pint.UnitRegistry()

# Find enthalpy of steam at 200°C and 1 atm
H = PropsSI('H', 'T', 473.15, 'P', 101325, 'Water')
# H ≈ 2875 kJ/kg
```

## Common Pitfalls
- Using gauge pressure instead of absolute pressure
- Forgetting to convert °C to K for CoolProp
- Assuming ideal gas behavior at high pressures
- Not checking if fluid is in two-phase region

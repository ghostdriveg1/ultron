---
name: Python Development
description: Write production-quality Python code following best practices and modern patterns
---

# Python Development Skill

## Trigger Patterns
- "write Python"
- "create Python script"
- "Python function"
- "Python class"
- "debug Python"

## Steps
1. **Understand requirements** — Parse the task into inputs, outputs, constraints
2. **Design API** — Define function signatures with type hints (Python 3.11+)
3. **Write Pydantic models** — Validate all inputs with `pydantic.BaseModel`
4. **Implement logic** — Follow SOLID principles, keep functions < 30 lines
5. **Add error handling** — Use specific exceptions, never bare `except`
6. **Write docstrings** — Google-style docstrings for all public functions
7. **Add type hints** — All parameters and return types annotated
8. **Test** — Write pytest tests with parametrize for edge cases
9. **Lint** — Pass ruff, mypy strict mode

## Example
```python
from pydantic import BaseModel, Field

class CalculationInput(BaseModel):
    values: list[float] = Field(..., min_length=1)
    method: str = Field(default="mean")

def calculate(input: CalculationInput) -> float:
    """Calculate aggregate statistic for given values."""
    if input.method == "mean":
        return sum(input.values) / len(input.values)
    raise ValueError(f"Unknown method: {input.method}")
```

## Common Pitfalls
- Mutable default arguments (`def f(x=[])`)
- Not using `pathlib.Path` for file operations
- Blocking async event loop with synchronous calls
- Missing `__init__.py` in packages

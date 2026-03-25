import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'ultron'))
print(f"PYTHONPATH: {sys.path}")
try:
    from packages.circuit_breaker.breaker import CircuitBreaker
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

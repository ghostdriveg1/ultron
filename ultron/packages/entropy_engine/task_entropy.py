from typing import Any

class TaskEntropyScorer:
    def score(self, task: Any) -> float:
        ambiguity = 15.0
        dependencies = 10.0
        
        op = getattr(task, "operation", "read") if hasattr(task, "operation") else "read"
        if op == "read":
            reversibility = 0.0
        elif op == "deploy":
            reversibility = 20.0
        else:
            reversibility = 10.0
            
        unknowns = 15.0
        
        return min(100.0, ambiguity + dependencies + reversibility + unknowns)

import json

class AlphaEvaluator:
    """Evaluates the fitness of prompt/code mutations."""
    
    async def evaluate_fitness(self, mutation_id: str, test_results: dict) -> float:
        # Simplistic heuristic for Phase 5
        score = 0.0
        if test_results.get("passed"):
            score += 50.0
            
        # Reward smaller diffs to avoid wild rewrites
        diff_size = test_results.get("diff_size_lines", 100)
        score += max(0, 50 - diff_size)
        
        return score

class PromptCrossover:
    """Performs genetic crossover operations on prompts."""
    
    def blend_prompts(self, prompt_a: str, prompt_b: str) -> str:
        # Simplistic crossover for Phase 5 template
        lines_a = prompt_a.splitlines()
        lines_b = prompt_b.splitlines()
        
        # Take first half of A, second half of B
        half_a = len(lines_a) // 2
        half_b = len(lines_b) // 2
        
        child_lines = lines_a[:half_a] + lines_b[half_b:]
        return "\n".join(child_lines)

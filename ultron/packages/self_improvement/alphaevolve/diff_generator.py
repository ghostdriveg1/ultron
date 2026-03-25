import difflib

class DiffGenerator:
    """Generates precise git-diff like outputs for proposed changes."""
    
    def generate_diff(self, original_content: str, new_content: str, filename: str) -> str:
        orig_lines = original_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            orig_lines, 
            new_lines, 
            fromfile=f"a/{filename}", 
            tofile=f"b/{filename}",
            n=3
        )
        return "".join(diff)

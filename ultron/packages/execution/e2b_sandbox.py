import time
from pydantic import BaseModel
from e2b import Sandbox

class SandboxResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int

class E2BSandboxManager:
    """Manages ephemeral code execution sandboxes."""
    
    async def run_code(self, code: str, language: str, timeout: int = 30) -> SandboxResult:
        start_time = time.time()
        
        try:
            sandbox = Sandbox()
            ext = ".py" if language == "python" else ".js"
            cmd_opts = "python" if language == "python" else "node"
            code_file = f"/home/user/main{ext}"
            
            sandbox.filesystem.write(code_file, code)
            
            process = sandbox.process.start_and_wait(
                f"{cmd_opts} {code_file}",
                timeout=timeout
            )
            
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.exit_code
            
            sandbox.close()
            
        except Exception as e:
            if "timeout" in str(e).lower():
                stdout = ""
                stderr = "Execution timed out."
                exit_code = -1
            else:
                stdout = ""
                stderr = f"Sandbox Exception: {str(e)}"
                exit_code = -2
                
        duration_ms = int((time.time() - start_time) * 1000)
        
        return SandboxResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration_ms
        )

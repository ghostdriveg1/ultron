import time
from e2b import Sandbox

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.runner_schema import RunnerInput, RunnerOutput

class RunnerTool(BaseTool):
    """Tool to execute code safely in an E2B sandbox."""
    input_schema = RunnerInput
    output_schema = RunnerOutput

    def __init__(self):
        super().__init__(
            name="run_code",
            description="Executes code in an isolated E2B cloud sandbox.",
            permission_level="GHOST_CONFIRM",
            requires_ghost_confirm=True
        )

    async def execute(self, params: RunnerInput) -> RunnerOutput:
        start_time = time.time()
        
        try:
            sandbox = Sandbox()
            # Write code to file and execute
            ext = ".py" if params.language == "python" else ".js"
            cmd_opts = "python" if params.language == "python" else "node"
            code_file = f"/home/user/main{ext}"
            
            sandbox.filesystem.write(code_file, params.code)
            
            process = sandbox.process.start_and_wait(
                f"{cmd_opts} {code_file}",
                timeout=params.timeout_seconds
            )
            
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.exit_code
            
            sandbox.close()
            
        except Exception as e:
            if "timeout" in str(e).lower():
                stdout = ""
                stderr = "Timeout"
                exit_code = -1
            else:
                stdout = ""
                stderr = f"Sandbox Exception: {str(e)}"
                exit_code = -2
                
        duration_ms = int((time.time() - start_time) * 1000)
        
        return RunnerOutput(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration_ms
        )

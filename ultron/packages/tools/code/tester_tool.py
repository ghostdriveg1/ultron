import subprocess
import json
import os

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.tester_schema import TesterInput, TesterOutput

class TesterTool(BaseTool):
    """Executes tests and parses the results."""
    input_schema = TesterInput
    output_schema = TesterOutput

    def __init__(self):
        super().__init__(
            name="run_tests",
            description="Runs unit tests using pytest or jest and returns structured results.",
            permission_level="ENTROPY_CHECKED"
        )

    async def execute(self, params: TesterInput) -> TesterOutput:
        passed = 0
        failed = 0
        coverage = 0.0
        failures = []

        if params.framework == "pytest":
            report_file = ".report.json"
            subprocess.run(["pytest", params.test_path, f"--json-report", f"--json-report-file={report_file}"], capture_output=True)
            
            if os.path.exists(report_file):
                with open(report_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        summary = data.get("summary", {})
                        passed = summary.get("passed", 0)
                        failed = summary.get("failed", 0)
                        
                        for test in data.get("tests", []):
                            if test.get("outcome") == "failed":
                                call = test.get("call", {})
                                crash = call.get("crash", {})
                                failures.append(f"{test.get('nodeid')}: {crash.get('message', 'Unknown Error')}")
                    except json.JSONDecodeError:
                        failures.append("Failed to parse pytest JSON report.")
                os.remove(report_file)
            else:
                failures.append("Pytest JSON report not generated.")

        elif params.framework == "jest":
            result = subprocess.run(["npx", "jest", params.test_path, "--json"], capture_output=True, text=True)
            try:
                data = json.loads(result.stdout)
                passed = data.get("numPassedTests", 0)
                failed = data.get("numFailedTests", 0)
                
                for test_result in data.get("testResults", []):
                    for assertion in test_result.get("assertionResults", []):
                        if assertion.get("status") == "failed":
                            failures.extend(assertion.get("failureMessages", []))
            except json.JSONDecodeError:
                failures.append(f"Failed to parse jest JSON report: {result.stderr[:200]}")
        else:
            failures.append(f"Unsupported framework: {params.framework}")
            
        return TesterOutput(
            passed=passed,
            failed=failed,
            coverage_percent=coverage,
            failures=failures
        )

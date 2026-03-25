import subprocess
with open("tsc_out2.txt", "w", encoding="utf-8") as out:
    res = subprocess.run(["npx.cmd", "tsc", "--noEmit"], cwd="website", capture_output=True, text=True)
    out.write(res.stdout)
    out.write(res.stderr)

with open("pytest_out2.txt", "w", encoding="utf-8") as out:
    res = subprocess.run(["pytest", "tests/test_phase5_fixes.py"], capture_output=True, text=True)
    out.write(res.stdout)
    out.write(res.stderr)

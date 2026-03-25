import subprocess
with open("final_test_output.txt", "w", encoding="utf-8") as out:
    res = subprocess.run(["pytest", "tests/test_phase5_fixes.py"], capture_output=True, text=True)
    out.write(str(res.stdout))
    out.write(str(res.stderr))

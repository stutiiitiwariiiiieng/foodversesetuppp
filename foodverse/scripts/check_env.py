"""Verify the dev environment. Run: python scripts/check_env.py"""
import importlib.util, os, shutil, subprocess, sys

ok = True
def report(name, passed, detail=""):
    global ok
    ok &= passed
    print(f"[{'OK' if passed else 'FAIL'}] {name} {detail}")

report("Python >= 3.8 (3.11 recommended)", sys.version_info >= (3, 8), sys.version.split()[0])
for tool in ("git", "node", "npm"):
    path = shutil.which(tool)
    ver = subprocess.run([tool, "--version"], capture_output=True, text=True).stdout.strip() if path else ""
    report(tool, bool(path), ver)
report("AWS CLI (optional)", True, "found" if shutil.which("aws") else "not installed (needed only for deployment)")
for mod in ("fastapi", "anthropic", "cv2", "uvicorn"):
    report(f"python module {mod}", importlib.util.find_spec(mod) is not None)
env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
has_key = os.path.exists(env) and "ANTHROPIC_API_KEY=your_key_here" not in open(env).read()
report("backend/.env with API key", has_key)
sys.exit(0 if ok else 1)

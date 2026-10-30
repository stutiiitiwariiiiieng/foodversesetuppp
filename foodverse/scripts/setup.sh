#!/usr/bin/env bash
# One-command setup for macOS / Linux
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements-dev.txt
[ -f backend/.env ] || cp backend/.env.example backend/.env
(cd frontend && npm install)
pre-commit install || true
python scripts/check_env.py || echo "Fix the FAIL items above (usually: add ANTHROPIC_API_KEY to backend/.env)"

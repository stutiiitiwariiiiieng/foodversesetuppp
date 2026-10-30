.PHONY: setup backend frontend test lint check docker
setup:    ; ./scripts/setup.sh
backend:  ; cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000
frontend: ; cd frontend && npm run dev
test:     ; cd backend && . .venv/bin/activate && pytest
lint:     ; cd backend && . .venv/bin/activate && ruff check .
check:    ; python3 scripts/check_env.py
docker:   ; docker compose up --build

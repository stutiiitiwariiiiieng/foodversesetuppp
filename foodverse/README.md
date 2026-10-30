# Food Verse AI

Multimodal food intelligence platform: meal recognition + nutrition, freshness detection,
kitchen hygiene video audit, cooking assistant, personalized meal plans.

**Stack:** React (Vite) · FastAPI · OpenCV · Claude vision/LLM

## Run backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

## Run frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 (Vite proxies `/api` to port 8000).

## Endpoints
| Method | Path | Input |
|---|---|---|
| POST | /api/food/analyze | image |
| POST | /api/freshness/check | image |
| POST | /api/hygiene/analyze | video |
| POST | /api/cooking/recipe | JSON |
| POST | /api/cooking/from-image | ingredient photo |
| POST | /api/audio/transcribe | audio (optional install) |
| POST | /api/kitchen/assist | form: message, history, optional image |
| POST | /api/mealplan/generate | JSON profile (`use_history` uses scanned meals) |
| GET | /api/history/meals, /api/history/summary | `days` query |

See `docs/MILESTONES.md` for how each milestone maps to the code.

## Quick start and testing
`./scripts/setup.sh`, `make check`, `make backend`, `make frontend`, `make test`. See `docs/REQUIREMENTS.md` and `docs/TEST_PLAN.md`.

See `docs/DEPLOY.md` for the full GitHub, Render and Vercel walkthrough.

## Deploy (AWS)
- Backend: package with Docker, run on EC2 / App Runner / ECS, store the key in Secrets Manager.
- Frontend: `npm run build`, upload `dist/` to S3 + CloudFront; set `CORS_ORIGINS`.

## Notes
Freshness, hygiene and calorie outputs are AI estimates, not safety guarantees.

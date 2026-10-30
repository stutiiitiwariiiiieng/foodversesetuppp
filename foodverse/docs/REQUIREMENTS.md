# Food Verse AI: Requirements and Technology Choices

## Functional requirements

| ID | Module (Epic) | Requirement | Endpoint / UI |
|---|---|---|---|
| FR-1 | Food Recognition & Nutrition | Identify dishes and items from a photo, any cuisine | POST /api/food/analyze, Meal scan |
| FR-2 | Food Recognition & Nutrition | Estimate calories, protein, carbs, fat and a 0-100 health score | same |
| FR-3 | Food Recognition & Nutrition | Cope with bad lighting, occlusion, large or odd image files | `app/utils.py` (validate, downscale, re-encode) |
| FR-4 | Food Recognition & Nutrition | Save each analyzed meal so other modules can use it | `app/db.py`, GET /api/history/* |
| FR-5 | Freshness | Classify Fresh / Moderately Fresh / Spoiled with visible signals and a safe-to-eat flag | POST /api/freshness/check, Freshness |
| FR-6 | Freshness | Give storage and use-it-soon advice to reduce waste | same |
| FR-7 | Hygiene Monitor | Sample frames from a kitchen video and check gloves, hair cap, apron, handling, surfaces | POST /api/hygiene/analyze, Kitchen hygiene |
| FR-8 | Hygiene Monitor | Produce risk level, score, violations by frame, alerts and recommendations | same |
| FR-9 | Smart Kitchen Assistant | Generate recipes with ingredients, steps, tips, timers, substitutions | POST /api/cooking/recipe, Recipes |
| FR-10 | Smart Kitchen Assistant | Answer mid-cook questions using conversation context and an optional photo; flag safety issues | POST /api/kitchen/assist, Kitchen assistant |
| FR-11 | Meal Planner | Compute targets from profile and goal; respect diet, allergies, dislikes | POST /api/mealplan/generate, Meal plan |
| FR-12 | Meal Planner | Adapt the plan to the meals the user actually scanned (`use_history`) and explain why | same |
| FR-13 | Integration | One dashboard summarizing scanned meals over the last 7 days | My week |

## Non-functional requirements
- **Reliability:** AI calls retry on transient errors; unreadable model output is retried once, then returns a clear 502.
- **Safety:** freshness, hygiene and calorie results always carry a disclaimer. They are estimates, not guarantees.
- **Reproducibility:** pinned Python dependencies, `.python-version`, `scripts/setup.sh`, `scripts/check_env.py`, Docker Compose, CI.
- **Testability:** all AI calls go through `ask_json`, so the test suite runs offline with a fake model.
- **Usability:** keyboard focus visible, responsive layout, plain-language errors.

## Libraries and why
| Need | Choice | Reason |
|---|---|---|
| API | FastAPI + Uvicorn | typed models, auto docs at /docs, async uploads |
| Vision and reasoning | Claude via `anthropic` SDK | one model covers recognition, freshness, hygiene reasoning, recipes, planning |
| Video and image handling | OpenCV (headless) | frame sampling, resize, re-encode |
| Storage | SQLite (stdlib) | zero setup; swap for PostgreSQL or DynamoDB in production |
| Frontend | React 18 + Vite | fast dev server, plain CSS, no heavy UI kit |
| Testing | pytest + httpx TestClient | offline tests with a mocked model |
| Quality | ruff, pre-commit, GitHub Actions | consistent style, CI on every push |

## Environment setup
```
./scripts/setup.sh      # venv, dependencies, .env, npm install
make check              # verifies tools, modules and API key
make backend            # terminal 1
make frontend           # terminal 2
make test               # backend tests (offline)
make docker             # or run everything in containers
```

# Test Plan and Demo Script

## Automated (backend/tests, run with `make test`)
| Area | Cases |
|---|---|
| Health | /health returns ok |
| Meal scan | nutrition returned and logged; `log=false` skips logging; corrupt file rejected (400); big image downscaled; non-image rejected |
| Freshness | status is one of the three classes |
| Hygiene | video frames sampled and report returned; non-video rejected |
| Recipes | recipe has steps |
| Kitchen assistant | text plus photo reaches the model as an image block; malformed history rejected |
| Meal plan | invalid profile (age 5) rejected with 422; valid profile returns targets |
| Integration | scan 2 meals, summary totals correct, plan prompt contains recent intake only when `use_history` is true; history can be cleared |

The model is faked in `conftest.py`, so these tests check wiring, validation and data flow. They do not measure AI accuracy.

## Manual accuracy check (needs an API key)
1. Run `./scripts/smoke_test.sh http://localhost:8000 some_food.jpg`.
2. Try 10 photos per module: varied lighting, cuisines, half-hidden food.
3. Freshness: test fresh, ripe and visibly spoiled samples. Confirm obviously moldy food is never "Fresh".
4. Hygiene: record a 20 to 30 second clip with and without gloves. Confirm the glove check changes.
5. Record failures and tune the prompts in each router's `SYSTEM` string.

## Demo script (about 5 minutes)
1. **Meal scan:** upload a plate, show macros and health score, mention it was logged.
2. **Freshness:** upload a fruit or vegetable, show the signals and storage tip.
3. **Hygiene:** upload a short kitchen clip, show the checklist and alerts.
4. **Recipes then Kitchen assistant:** generate a recipe, then ask "is this browned enough?" with a photo.
5. **Meal plan:** tick "adjust using the meals I scanned" and show the "Why" lines.
6. **My week:** show the dashboard tying it together.

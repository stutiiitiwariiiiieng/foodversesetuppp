# Milestones mapped to the code

Python 3.10 or newer is required (the code uses modern type hints). 3.11 is recommended.

| Milestone / Activity | What it covers | Where in the code | How to show it |
|---|---|---|---|
| **1.1** requirements.txt | Dependencies grouped by category: backend, LLM, computer vision, audio (optional), data | `backend/requirements.txt`, `requirements-audio.txt`, `requirements-dev.txt` | open the files |
| **1.2** environment | Virtual environment, install, verification | `scripts/setup.sh`, `scripts/check_env.py`, `make check` | run `make check`, then open http://localhost:8000/health |
| **2.1** food detection | Upload, resize, light normalization, classification, structured output | `app/utils.py` (`prepare_image`), `app/routers/food.py` | Meal scan tab |
| **2.2** nutrition and health score | Items mapped to reference values, totals recomputed, 0-100 score from macro balance, calorie density and portion size | `app/nutrition.py` | Meal scan result shows macro split and "checked against reference" |
| **3.1** freshness features | Resize, CLAHE lighting correction, denoise; color ratios, pale-patch (mold-like) ratio, texture sharpness, edge density, image quality warnings | `app/features.py` | Freshness result shows "Measured: ..." |
| **3.2** freshness classification | Score to Fresh / Moderately Fresh / Spoiled, takes the more cautious of rule and AI verdict, confidence %, safety message | `app/scoring.py` (`finalize_freshness`), `app/routers/freshness.py` | Freshness tab |
| **4.1** hygiene | Frame sampling, checks for gloves, hair cap, apron, handling, surfaces, cross-contamination; weighted compliance score, risk level, alerts | `app/routers/hygiene.py`, `app/scoring.py` (`hygiene_compliance`) | Kitchen hygiene tab |
| **4.2** smart kitchen | Recipes from text or from an ingredient photo; live assistant with context, photo and voice | `app/routers/cooking.py`, `kitchen.py`, `audio.py` | Recipes and Kitchen assistant tabs |
| **5.1** profile processing | Validated profile, allergies and dislikes, optional use of scanned meals | `app/routers/mealplan.py` (`Profile`) | Meal plan form |
| **5.2** plan generation | Calorie and macro targets computed from BMR and goal, 1 to 7 day plan, alternatives per meal, allergen cross-check, adaptation to scanned meals | `app/scoring.py` (`targets`, `allergen_warnings`), `mealplan.py` | Meal plan result |
| **6.1** run the app | Backend plus REST integration | `make backend`, `docs/DEPLOY.md` | /docs page lists every endpoint |
| **6.2** React dashboard | Seven panels plus My week dashboard | `frontend/src/` | `make frontend` |
| **6.3** validate and edge cases | Corrupt, huge, dark, blurry, low-resolution inputs; bad profiles; unreadable AI output | `backend/tests/`, `docs/TEST_PLAN.md` | `make test` |

## Honest notes for your report
- Recognition, freshness and hygiene judgements come from a vision-language model. The OpenCV features and the rule-based scores (nutrition, hygiene, freshness mapping, calorie targets) sit around it to make results consistent and explainable.
- The nutrition reference table is a small approximate starter set, not a full database.
- All outputs are estimates and carry disclaimers.
- Audio input needs the optional `requirements-audio.txt` install; without it the microphone button shows a clear message.

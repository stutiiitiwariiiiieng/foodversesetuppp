#!/usr/bin/env bash
# Live smoke test against a running backend (uses the real AI, so needs an API key).
# Usage: ./scripts/smoke_test.sh [base_url] [food.jpg]
set -euo pipefail
BASE="${1:-http://localhost:8000}"
IMG="${2:-}"
echo "health:"; curl -fsS "$BASE/health"; echo
echo "recipe:"; curl -fsS -X POST "$BASE/api/cooking/recipe" -H 'Content-Type: application/json' \
  -d '{"query":"vegetable upma","servings":2}' | head -c 300; echo
echo "meal plan:"; curl -fsS -X POST "$BASE/api/mealplan/generate" -H 'Content-Type: application/json' \
  -d '{"age":25,"sex":"female","height_cm":165,"weight_kg":60,"days":1}' | head -c 300; echo
if [ -n "$IMG" ]; then
  echo "food:"; curl -fsS -F "file=@$IMG" "$BASE/api/food/analyze" | head -c 300; echo
  echo "freshness:"; curl -fsS -F "file=@$IMG" "$BASE/api/freshness/check" | head -c 300; echo
fi
echo "ALL OK"

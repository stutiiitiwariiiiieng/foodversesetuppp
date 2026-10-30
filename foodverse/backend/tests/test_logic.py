"""Unit tests for the rule-based logic (no AI, no HTTP)."""
import cv2
import numpy as np

from app import features, nutrition, scoring


def test_health_score_balanced_beats_junk():
    good = nutrition.health_score({"calories": 500, "protein_g": 30, "carbs_g": 55, "fat_g": 16}, 450)
    junk = nutrition.health_score({"calories": 1100, "protein_g": 12, "carbs_g": 90, "fat_g": 70}, 300)
    assert 0 <= junk["score"] < good["score"] <= 100
    assert junk["calorie_density_kcal_per_100g"] > 300 and junk["notes"]


def test_reconcile_replaces_wild_estimates_and_recomputes_totals():
    a = {"items": [{"name": "Plain rice", "grams": 200, "calories": 900, "protein_g": 1, "carbs_g": 1, "fat_g": 1}],
         "totals": {"calories": 1, "protein_g": 0, "carbs_g": 0, "fat_g": 0}, "health_score": 50}
    out = nutrition.reconcile(a)
    assert out["items"][0]["source"] == "reference" and out["items"][0]["calories"] == 260
    assert out["totals"]["calories"] == 260 and out["ai_health_score"] == 50
    assert 0 <= out["health_score"] <= 100


def test_hygiene_scoring_and_risk():
    all_pass = [{"item": n, "status": "pass"} for n in scoring.HYGIENE_WEIGHTS]
    assert scoring.hygiene_compliance(all_pass)["risk_level"] == "low"
    no_gloves = [{"item": n, "status": "fail" if n == "gloves" else "pass"} for n in scoring.HYGIENE_WEIGHTS]
    r = scoring.hygiene_compliance(no_gloves)
    assert r["overall_score"] == 75 and r["risk_level"] == "medium"
    assert any("CRITICAL" in a for a in r["rule_alerts"])
    assert scoring.hygiene_compliance([])["insufficient_evidence"] is True


def test_freshness_takes_the_more_cautious_verdict():
    out = scoring.finalize_freshness({"freshness_score": 90, "status": "Spoiled", "confidence": "high"})
    assert out["status"] == "Spoiled" and out["safe_to_eat"] is False
    out = scoring.finalize_freshness({"freshness_score": 85, "status": "Fresh"}, {"pale_patch_ratio": 0.3})
    assert out["status"] == "Moderately Fresh" and out["cautions"]
    out = scoring.finalize_freshness({"freshness_score": 20, "status": "Fresh"})
    assert out["status"] == "Spoiled"


def test_targets_follow_goal():
    p = {"age": 30, "sex": "male", "height_cm": 175, "weight_kg": 75, "activity": "moderate"}
    base = scoring.targets({**p, "goal": "maintain"})["calories"]
    assert scoring.targets({**p, "goal": "lose"})["calories"] < base < scoring.targets({**p, "goal": "gain"})["calories"]


def test_allergen_check_avoids_false_positives():
    plan = {"days": [{"meals": [{"name": "Eggplant curry", "description": "with rice"},
                                {"name": "Paneer wrap", "description": "", "alternatives": [{"name": "Peanut chikki"}]}]}],
            "grocery_list": ["Wheat flour"]}
    w = scoring.allergen_warnings(plan, "egg, dairy, peanuts")
    allergens = {x["allergen"] for x in w}
    assert "dairy" in allergens and "peanuts" in allergens and "egg" not in allergens


def test_feature_extraction_separates_fresh_from_rotten():
    fresh = np.zeros((200, 200, 3), np.uint8); fresh[:] = (40, 180, 60)       # green
    rotten = np.zeros((200, 200, 3), np.uint8); rotten[:] = (20, 40, 70)      # dark brown
    f1, f2 = features.extract(fresh), features.extract(rotten)
    assert f1["green_ratio"] > 0.8 and f2["brown_dark_ratio"] > 0.8
    assert "dark" in " ".join(features.quality_warnings(np.full((100, 100, 3), 10, np.uint8))).lower()
    assert cv2.imencode(".jpg", fresh)[0]

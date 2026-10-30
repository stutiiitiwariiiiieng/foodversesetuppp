"""Rule-based logic shared by modules: hygiene compliance, freshness safety,
calorie targets, allergen checks. Pure Python so it is easy to unit-test."""
import re

# ---------- Activity 4.1: hygiene compliance ----------
HYGIENE_WEIGHTS = {"gloves": 25, "hair cap": 20, "apron": 10, "food handling": 20,
                   "surface cleanliness": 15, "cross-contamination": 10}
CRITICAL = {"gloves", "food handling", "cross-contamination"}


def hygiene_compliance(checks: list) -> dict:
    status = {str(c.get("item", "")).strip().lower(): str(c.get("status", "unknown")).lower() for c in checks}
    earned, unknown_w, rows, alerts = 0.0, 0, [], []
    for name, w in HYGIENE_WEIGHTS.items():
        st = status.get(name, "unknown")
        pts = w if st == "pass" else 0 if st == "fail" else w / 2
        if st not in ("pass", "fail"):
            unknown_w += w
        earned += pts
        rows.append({"item": name, "weight": w, "status": st, "points": pts})
        if st == "fail":
            alerts.append(f"{'CRITICAL: ' if name in CRITICAL else ''}{name} not compliant")
    score = round(earned)
    critical_fail = any(r["status"] == "fail" and r["item"] in CRITICAL for r in rows)
    risk = "low" if score >= 80 else "medium" if score >= 55 else "high"
    if critical_fail and risk == "low":
        risk = "medium"
    return {"overall_score": score, "risk_level": risk, "compliance_breakdown": rows,
            "rule_alerts": alerts, "insufficient_evidence": unknown_w >= 50}


# ---------- Activity 3.2: freshness classification ----------
RANK = {"Fresh": 0, "Moderately Fresh": 1, "Spoiled": 2}
SAFETY = {
    "Fresh": "Safe to eat. Store properly to keep it fresh.",
    "Moderately Fresh": "Use soon and cook thoroughly. Inspect for smell and texture before eating.",
    "Spoiled": "Do not eat. Discard it and clean the container or surface it touched.",
}
CONF_PCT = {"low": 40, "medium": 70, "high": 90}


def finalize_freshness(out: dict, feats: dict | None = None) -> dict:
    score = int(max(0, min(100, float(out.get("freshness_score") or 0))))
    by_score = "Fresh" if score >= 70 else "Moderately Fresh" if score >= 40 else "Spoiled"
    ai = out.get("status") if out.get("status") in RANK else by_score
    status = max(by_score, ai, key=lambda s: RANK[s])  # the more cautious of the two
    notes = []
    if feats and feats.get("pale_patch_ratio", 0) > 0.12 and status == "Fresh":
        status, score = "Moderately Fresh", min(score, 69)
        notes.append("Pale patches detected in the image (possible mold). Inspect manually.")
    out.update(status=status, freshness_score=score,
               confidence_pct=CONF_PCT.get(out.get("confidence"), 50),
               safe_to_eat=status != "Spoiled" and out.get("safe_to_eat", True) is not False,
               safety_recommendation=SAFETY[status], cautions=notes)
    return out


# ---------- Activity 5.1/5.2: targets and allergen safety ----------
ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}


def targets(p: dict) -> dict:
    sex = str(p.get("sex", "")).lower()
    offset = 5 if sex == "male" else -161 if sex == "female" else -78
    bmr = 10 * p["weight_kg"] + 6.25 * p["height_cm"] - 5 * p["age"] + offset
    tdee = bmr * ACTIVITY.get(str(p.get("activity", "moderate")).lower(), 1.55)
    goal = str(p.get("goal", "maintain")).lower()
    kcal = tdee - 500 if goal == "lose" else tdee + 400 if goal == "gain" else tdee
    kcal = max(kcal, 1500 if sex == "male" else 1200 if sex == "female" else 1350)
    protein = p["weight_kg"] * (1.8 if goal in ("lose", "gain") else 1.6)
    fat = kcal * 0.25 / 9
    carbs = max(0, (kcal - protein * 4 - fat * 9) / 4)
    return {"calories": round(kcal), "protein_g": round(protein), "carbs_g": round(carbs),
            "fat_g": round(fat), "bmr": round(bmr), "tdee": round(tdee)}


ALLERGEN_TERMS = {
    "dairy": ["milk", "cheese", "paneer", "curd", "yogurt", "butter", "ghee", "cream"],
    "lactose": ["milk", "cheese", "paneer", "curd", "yogurt", "butter", "cream"],
    "gluten": ["wheat", "bread", "roti", "chapati", "pasta", "flour", "naan", "semolina", "rava"],
    "nut": ["almond", "cashew", "walnut", "pistachio", "peanut", "hazelnut"],
    "peanut": ["peanut", "groundnut"], "shellfish": ["shrimp", "prawn", "crab", "lobster"],
    "egg": ["egg"], "soy": ["soy", "tofu"], "fish": ["fish", "salmon", "tuna"],
}


def allergen_warnings(plan: dict, allergies: str) -> list:
    tokens = [t.strip().lower() for t in re.split(r"[,;/]|\band\b", allergies or "") if t.strip()]
    texts = []
    for d in plan.get("days", []):
        for m in d.get("meals", []):
            texts.append((m.get("name", ""), f"{m.get('name', '')} {m.get('description', '')}"))
            for a in m.get("alternatives", []) or []:
                texts.append((a.get("name", ""), a.get("name", "")))
    texts += [(g, g) for g in plan.get("grocery_list", [])]
    found = []
    for t in tokens:
        base = t[:-1] if t.endswith("s") else t
        terms = set(ALLERGEN_TERMS.get(t, []) + ALLERGEN_TERMS.get(base, []) + [t, base])
        for label, text in texts:
            if any(re.search(rf"\b{re.escape(x)}s?\b", text.lower()) for x in terms):
                found.append({"allergen": t, "found_in": label})
    return found

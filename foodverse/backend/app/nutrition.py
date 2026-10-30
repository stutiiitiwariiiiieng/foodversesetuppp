"""Activity 2.2: reference-based nutrition checks and rule-based health scoring."""

# Approximate typical values per 100 g as eaten: (kcal, protein_g, carbs_g, fat_g).
# Starter table for sanity-checking AI estimates. For production, replace with a
# USDA FoodData Central / IFCT lookup.
REFERENCE = {
    "rice": (130, 2.7, 28, 0.3), "biryani": (150, 6, 20, 5), "roti": (297, 9, 46, 7),
    "chapati": (297, 9, 46, 7), "paratha": (326, 7, 45, 13), "naan": (290, 9, 50, 6),
    "bread": (265, 9, 49, 3.2), "dal": (116, 9, 20, 0.4), "sambar": (50, 2.5, 8, 1),
    "idli": (130, 3.5, 27, 0.6), "dosa": (168, 4, 29, 3.7), "paneer": (296, 18, 3.6, 23),
    "chicken": (190, 27, 0, 8), "egg": (155, 13, 1.1, 11), "fish": (206, 22, 0, 12),
    "potato": (87, 1.9, 20, 0.1), "salad": (20, 1.2, 3.6, 0.2), "curd": (61, 3.5, 4.7, 3.3),
    "yogurt": (61, 3.5, 4.7, 3.3), "milk": (61, 3.2, 4.8, 3.3), "banana": (89, 1.1, 23, 0.3),
    "apple": (52, 0.3, 14, 0.2), "pasta": (158, 5.8, 31, 0.9), "pizza": (266, 11, 33, 10),
    "burger": (295, 17, 30, 14), "fries": (312, 3.4, 41, 15), "samosa": (262, 3.5, 24, 17),
    "oats": (71, 2.5, 12, 1.5), "curry": (120, 7, 6, 7), "soup": (40, 2, 6, 1),
}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def lookup(name: str):
    """Longest reference key contained in the item name, or None."""
    n = (name or "").lower()
    hits = [k for k in REFERENCE if k in n]
    return max(hits, key=len) if hits else None


def health_score(totals: dict, total_grams=None) -> dict:
    """0-100 score from macro balance, calorie density and meal size."""
    p, c, f = (_num(totals.get(k)) or 0 for k in ("protein_g", "carbs_g", "fat_g"))
    kcal = _num(totals.get("calories")) or 0
    macro_kcal = 4 * p + 4 * c + 9 * f
    notes = []
    if macro_kcal <= 0:
        return {"score": 0, "macro_split_pct": None, "calorie_density_kcal_per_100g": None,
                "penalties": {}, "notes": ["No nutrition data to score"]}
    pct = {"protein": 400 * p / macro_kcal, "carbs": 400 * c / macro_kcal, "fat": 900 * f / macro_kcal}

    def out_of_range(v, lo, hi, below_w, above_w):
        return (lo - v) * below_w if v < lo else (v - hi) * above_w if v > hi else 0

    macro_pen = min(40, out_of_range(pct["protein"], 12, 30, 1.0, 0.5)
                    + out_of_range(pct["carbs"], 40, 60, 0.6, 0.6)
                    + out_of_range(pct["fat"], 20, 35, 0.8, 0.8))
    if pct["protein"] < 12:
        notes.append("Low in protein")
    if pct["carbs"] > 60:
        notes.append("Carbohydrate heavy")
    if pct["fat"] > 35:
        notes.append("High in fat")

    density = None
    density_pen = 0
    g = _num(total_grams)
    if g and g > 0:
        density = round(kcal / g * 100, 1)
        density_pen = min(25, max(0, (density - 150) * 0.12))
        if density_pen > 5:
            notes.append("Energy-dense: small portion carries many calories")

    portion_pen = min(15, max(0, (kcal - 700) * 0.05)) if kcal > 700 else (5 if 0 < kcal < 150 else 0)
    if kcal > 900:
        notes.append("Large meal")

    score = round(max(0, min(100, 100 - macro_pen - density_pen - portion_pen)))
    return {"score": score, "macro_split_pct": {k: round(v, 1) for k, v in pct.items()},
            "calorie_density_kcal_per_100g": density,
            "penalties": {"macro": round(macro_pen, 1), "density": round(density_pen, 1),
                          "portion": round(portion_pen, 1)},
            "notes": notes}


def reconcile(analysis: dict, tolerance: float = 0.5) -> dict:
    """Map items to reference profiles, fix wild AI estimates, recompute totals and score."""
    items = analysis.get("items") or []
    total_g, checked = 0.0, 0
    for it in items:
        g = _num(it.get("grams"))
        if g:
            total_g += g
        key = lookup(it.get("name", ""))
        it["source"] = "ai"
        if g and key:
            ref, f = REFERENCE[key], g / 100
            expected = ref[0] * f
            ai_kcal = _num(it.get("calories")) or 0
            checked += 1
            if expected and abs(ai_kcal - expected) / expected > tolerance:
                it.update(calories=round(expected), protein_g=round(ref[1] * f, 1),
                          carbs_g=round(ref[2] * f, 1), fat_g=round(ref[3] * f, 1), source="reference")
    if items:
        analysis["totals"] = {
            "calories": round(sum(_num(i.get("calories")) or 0 for i in items)),
            "protein_g": round(sum(_num(i.get("protein_g")) or 0 for i in items), 1),
            "carbs_g": round(sum(_num(i.get("carbs_g")) or 0 for i in items), 1),
            "fat_g": round(sum(_num(i.get("fat_g")) or 0 for i in items), 1),
        }
    sb = health_score(analysis.get("totals", {}), total_g or None)
    analysis["ai_health_score"] = analysis.get("health_score")
    analysis["health_score"] = sb["score"]
    analysis["score_breakdown"] = sb
    analysis["reference_checked_items"] = checked
    return analysis

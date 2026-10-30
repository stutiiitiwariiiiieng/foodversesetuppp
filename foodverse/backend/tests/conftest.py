import copy
import os

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

CANNED = {
    "nutrition analyst": {
        "dish": "Dal and rice", "cuisine": "Indian",
        "items": [
            {"name": "Dal", "portion": "1 bowl", "grams": 250, "calories": 180, "protein_g": 10,
             "carbs_g": 25, "fat_g": 5},
            {"name": "Steamed rice", "portion": "1 cup", "grams": 200, "calories": 340, "protein_g": 8,
             "carbs_g": 60, "fat_g": 4}],
        "totals": {"calories": 520, "protein_g": 18, "carbs_g": 85, "fat_g": 9},
        "health_score": 78, "health_notes": "Balanced", "confidence": "medium", "disclaimer": "x"},
    "freshness from a photo": {
        "food": "Spinach", "status": "Moderately Fresh", "freshness_score": 55, "confidence": "medium",
        "safe_to_eat": True, "indicators": [{"signal": "Color", "observation": "slight yellowing",
                                             "severity": "warning"}],
        "recommendation": "Cook today", "storage_tip": "Refrigerate", "disclaimer": "x"},
    "audit kitchen hygiene": {
        "overall_score": 64, "risk_level": "medium",
        "checks": [{"item": "Gloves", "status": "fail", "evidence": "bare hands"},
                   {"item": "Hair cap", "status": "pass", "evidence": "worn"},
                   {"item": "Apron", "status": "pass", "evidence": "worn"},
                   {"item": "Food handling", "status": "pass", "evidence": "ok"},
                   {"item": "Surface cleanliness", "status": "pass", "evidence": "clean"},
                   {"item": "Cross-contamination", "status": "unknown", "evidence": "n/a"}],
        "violations": [{"frame": 2, "description": "No gloves"}], "alerts": ["Gloves missing"],
        "recommendations": ["Use gloves"], "disclaimer": "x"},
    "cooking coach": {
        "title": "Palak paneer", "servings": 2, "prep_minutes": 10, "cook_minutes": 20,
        "ingredients": [{"item": "Spinach", "quantity": "250 g"}],
        "detected_ingredients": ["spinach"],
        "steps": [{"step": "Blanch spinach", "tip": "Ice bath", "timer_minutes": 2}],
        "substitutions": [], "safety_notes": []},
    "live kitchen assistant": {
        "reply": "Lower the heat.", "next_action": "Stir", "timer_minutes": 3,
        "safety_flag": False, "safety_note": ""},
    "meal planner": {
        "daily_targets": {"calories": 1900, "protein_g": 90, "carbs_g": 240, "fat_g": 55},
        "days": [{"day": "Day 1", "meals": [{"type": "Breakfast", "name": "Oats", "calories": 350,
                                              "protein_g": 15, "description": "Oats with milk", "why": "w",
                                              "alternatives": [{"name": "Poha", "calories": 330,
                                                                "protein_g": 9}]}],
                  "total_calories": 1900}],
        "grocery_list": ["Oats"], "notes": [], "disclaimer": "x"},
}


class Recorder:
    def __init__(self):
        self.calls = []

    def text_of_last(self) -> str:
        return " ".join(b.get("text", "") for b in self.calls[-1][1] if b.get("type") == "text")


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch, tmp_path):
    """Replace the Claude call in every router so tests are offline and deterministic."""
    monkeypatch.setenv("FOODVERSE_DB", str(tmp_path / "test.db"))
    rec = Recorder()

    def fake(system, content, max_tokens=1500):
        rec.calls.append((system, content))
        for key, val in CANNED.items():
            if key in system:
                return copy.deepcopy(val)
        raise AssertionError("no canned response for prompt")

    from app.routers import cooking, food, freshness, hygiene, kitchen, mealplan
    for m in (cooking, food, freshness, hygiene, kitchen, mealplan):
        monkeypatch.setattr(m, "ask_json", fake)
    return rec


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def jpeg() -> bytes:
    img = np.random.randint(0, 255, (120, 160, 3), dtype=np.uint8)
    return cv2.imencode(".jpg", img)[1].tobytes()

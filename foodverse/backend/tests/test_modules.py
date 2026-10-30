import cv2
import numpy as np
import pytest


def test_food_analyze_returns_nutrition_and_logs(client, jpeg):
    r = client.post("/api/food/analyze", files={"file": ("m.jpg", jpeg, "image/jpeg")})
    assert r.status_code == 200
    d = r.json()
    assert d["totals"]["calories"] == 520 and d["logged"] is True and "meal_id" in d


def test_food_log_can_be_disabled(client, jpeg):
    client.post("/api/food/analyze?log=false", files={"file": ("m.jpg", jpeg, "image/jpeg")})
    assert client.get("/api/history/summary").json()["meal_count"] == 0


def test_corrupt_image_is_rejected(client):
    r = client.post("/api/food/analyze", files={"file": ("m.jpg", b"not an image", "image/jpeg")})
    assert r.status_code == 400


def test_large_image_is_downscaled(client):
    big = cv2.imencode(".jpg", np.zeros((4000, 3000, 3), np.uint8))[1].tobytes()
    from app.utils import prepare_image
    out = prepare_image(big)
    h, w = cv2.imdecode(np.frombuffer(out, np.uint8), 1).shape[:2]
    assert max(h, w) <= 1568


def test_freshness_check(client, jpeg):
    r = client.post("/api/freshness/check", files={"file": ("s.jpg", jpeg, "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["status"] in {"Fresh", "Moderately Fresh", "Spoiled"}


def test_hygiene_video(client, tmp_path):
    path = tmp_path / "k.avi"
    w = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (64, 64))
    for _ in range(20):
        w.write(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
    w.release()
    if not path.exists() or path.stat().st_size == 0:
        pytest.skip("OpenCV build cannot write MJPG video")
    r = client.post("/api/hygiene/analyze",
                    files={"file": ("k.avi", path.read_bytes(), "video/x-msvideo")})
    assert r.status_code == 200
    assert r.json()["frames_analyzed"] > 0 and r.json()["risk_level"] == "medium"


def test_cooking_recipe(client):
    r = client.post("/api/cooking/recipe", json={"query": "palak paneer"})
    assert r.status_code == 200 and r.json()["steps"]


def test_kitchen_assist_text_and_photo(client, jpeg, fake_llm):
    r = client.post("/api/kitchen/assist", data={"message": "Is the onion done?",
                    "history": '[{"role":"user","text":"hi"}]', "recipe_context": "Dal"},
                    files={"file": ("p.jpg", jpeg, "image/jpeg")})
    assert r.status_code == 200 and r.json()["reply"]
    assert any(b["type"] == "image" for b in fake_llm.calls[-1][1])


def test_kitchen_rejects_bad_history(client):
    r = client.post("/api/kitchen/assist", data={"message": "hi", "history": "{oops"})
    assert r.status_code == 400


def test_mealplan_validates_profile(client):
    bad = {"age": 5, "sex": "male", "height_cm": 170, "weight_kg": 60}
    assert client.post("/api/mealplan/generate", json=bad).status_code == 422


def test_mealplan_generate(client):
    p = {"age": 25, "sex": "female", "height_cm": 165, "weight_kg": 60}
    r = client.post("/api/mealplan/generate", json=p)
    assert r.status_code == 200 and r.json()["daily_targets"]["calories"] > 0


def test_food_response_has_score_breakdown_and_totals(client, jpeg):
    d = client.post("/api/food/analyze", files={"file": ("m.jpg", jpeg, "image/jpeg")}).json()
    assert d["totals"]["calories"] == 520 and d["score_breakdown"]["macro_split_pct"]
    assert d["reference_checked_items"] == 2 and "image_quality" in d


def test_freshness_includes_features_and_safety(client, jpeg):
    d = client.post("/api/freshness/check", files={"file": ("s.jpg", jpeg, "image/jpeg")}).json()
    assert d["features"]["texture_sharpness"] >= 0 and d["safety_recommendation"] and d["confidence_pct"] == 70


def test_cooking_from_ingredient_photo(client, jpeg):
    r = client.post("/api/cooking/from-image", data={"servings": "2"}, files={"file": ("i.jpg", jpeg, "image/jpeg")})
    assert r.status_code == 200 and r.json()["detected_ingredients"] == ["spinach"]


def test_mealplan_targets_are_computed_and_allergens_flagged(client):
    p = {"age": 25, "sex": "female", "height_cm": 165, "weight_kg": 60, "goal": "lose", "allergies": "dairy"}
    d = client.post("/api/mealplan/generate", json=p).json()
    assert d["daily_targets"]["calories"] != 1900          # replaced by computed value
    assert d["allergen_warnings"] and d["days"][0]["meals"][0]["alternatives"]


def test_audio_transcribe(client, monkeypatch):
    from app.routers import audio
    monkeypatch.setattr(audio, "transcribe_bytes", lambda data, suffix=".webm": "add more salt")
    r = client.post("/api/audio/transcribe", files={"file": ("v.webm", b"123", "audio/webm")})
    assert r.status_code == 200 and r.json()["text"] == "add more salt"
    assert client.post("/api/audio/transcribe", files={"file": ("a.txt", b"x", "text/plain")}).status_code == 400

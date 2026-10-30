"""End-to-end pipeline: scan meals -> history -> personalized meal plan."""


def test_scanned_meals_flow_into_meal_plan(client, jpeg, fake_llm):
    for _ in range(2):
        r = client.post("/api/food/analyze", files={"file": ("m.jpg", jpeg, "image/jpeg")})
        assert r.status_code == 200

    s = client.get("/api/history/summary").json()
    assert s["meal_count"] == 2 and s["total_calories"] == 1040

    profile = {"age": 30, "sex": "male", "height_cm": 175, "weight_kg": 80,
               "goal": "lose", "use_history": True}
    assert client.post("/api/mealplan/generate", json=profile).status_code == 200
    sent = fake_llm.text_of_last()
    assert "Recent intake" in sent and "Dal and rice" in sent and "use_history" not in sent


def test_plan_without_history_flag_ignores_log(client, jpeg, fake_llm):
    client.post("/api/food/analyze", files={"file": ("m.jpg", jpeg, "image/jpeg")})
    client.post("/api/mealplan/generate", json={"age": 30, "sex": "male", "height_cm": 175, "weight_kg": 80})
    assert "Recent intake" not in fake_llm.text_of_last()


def test_history_can_be_cleared(client, jpeg):
    client.post("/api/food/analyze", files={"file": ("m.jpg", jpeg, "image/jpeg")})
    assert client.delete("/api/history/meals").json() == {"cleared": True}
    assert client.get("/api/history/meals").json() == []

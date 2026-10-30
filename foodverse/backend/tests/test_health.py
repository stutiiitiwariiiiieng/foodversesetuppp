from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_food_rejects_non_image():
    r = client.post("/api/food/analyze", files={"file": ("a.txt", b"hi", "text/plain")})
    assert r.status_code == 400


def test_hygiene_rejects_non_video():
    r = client.post("/api/hygiene/analyze", files={"file": ("a.txt", b"hi", "text/plain")})
    assert r.status_code == 400

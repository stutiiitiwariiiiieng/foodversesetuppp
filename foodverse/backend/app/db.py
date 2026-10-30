"""Tiny SQLite store so modules can share data (scanned meals feed the meal planner)."""
import os
import sqlite3
from contextlib import contextmanager

SCHEMA = """CREATE TABLE IF NOT EXISTS meals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  dish TEXT, calories REAL, protein_g REAL, carbs_g REAL, fat_g REAL, health_score INTEGER)"""


def _path() -> str:
    return os.getenv("FOODVERSE_DB", os.path.join(os.path.dirname(__file__), "..", "data", "foodverse.db"))


@contextmanager
def conn():
    path = _path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    c.execute(SCHEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()


def add_meal(analysis: dict) -> int:
    t = analysis.get("totals", {})
    with conn() as c:
        cur = c.execute(
            "INSERT INTO meals (dish, calories, protein_g, carbs_g, fat_g, health_score) VALUES (?,?,?,?,?,?)",
            (analysis.get("dish"), t.get("calories", 0), t.get("protein_g", 0),
             t.get("carbs_g", 0), t.get("fat_g", 0), analysis.get("health_score")),
        )
        return cur.lastrowid


def list_meals(days: int = 7) -> list[dict]:
    with conn() as c:
        rows = c.execute(
            "SELECT * FROM meals WHERE ts >= datetime('now', ?) ORDER BY ts DESC", (f"-{int(days)} days",)
        ).fetchall()
    return [dict(r) for r in rows]


def summary(days: int = 7) -> dict:
    meals = list_meals(days)
    n = len(meals)
    tot = lambda k: round(sum(m[k] or 0 for m in meals), 1)  # noqa: E731
    scores = [m["health_score"] for m in meals if m["health_score"] is not None]
    return {
        "days": days, "meal_count": n,
        "total_calories": tot("calories"), "total_protein_g": tot("protein_g"),
        "total_carbs_g": tot("carbs_g"), "total_fat_g": tot("fat_g"),
        "avg_health_score": round(sum(scores) / len(scores), 1) if scores else None,
        "recent_dishes": [m["dish"] for m in meals[:8]],
    }


def clear() -> None:
    with conn() as c:
        c.execute("DELETE FROM meals")

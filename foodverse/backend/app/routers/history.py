from fastapi import APIRouter, Query

from app import db

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/meals")
def meals(days: int = Query(7, ge=1, le=90)):
    return db.list_meals(days)


@router.get("/summary")
def summary(days: int = Query(7, ge=1, le=90)):
    return db.summary(days)


@router.delete("/meals")
def clear():
    db.clear()
    return {"cleared": True}

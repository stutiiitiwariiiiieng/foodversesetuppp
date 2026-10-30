import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio, cooking, food, freshness, history, hygiene, kitchen, mealplan

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Food Verse AI", version="1.1.0")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

for r in (food, freshness, hygiene, cooking, kitchen, audio, mealplan, history):
    app.include_router(r.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}

import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import db
from app.config import CORS_ORIGINS, TELEGRAM_BOT_TOKEN
from app.scheduler import start_scheduler, stop_scheduler
from app.telegram_bot import start_bot, stop_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("niche.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    start_scheduler()
    if TELEGRAM_BOT_TOKEN:
        await start_bot()
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled")
    yield
    if TELEGRAM_BOT_TOKEN:
        await stop_bot()
    stop_scheduler()


app = FastAPI(title="Niche", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/summaries")
def api_summaries(
    feed: Optional[str] = Query(default=None, pattern="^(research|market)$"),
    since_hours: Optional[int] = None,
    limit: int = 50,
):
    return db.get_summaries(feed=feed, since_hours=since_hours, limit=limit)


@app.get("/api/niche-ideas/latest")
def api_niche_idea_latest():
    idea = db.get_niche_idea(date.today().isoformat())
    if idea is None:
        raise HTTPException(status_code=404, detail="No idea generated yet today")
    return idea


@app.get("/api/investors")
def api_investors(days: int = 30):
    return db.get_investors(days=days)


class SaveRequest(BaseModel):
    summary_id: int


@app.post("/api/saved")
def api_save(req: SaveRequest):
    db.save_summary(req.summary_id)
    return {"ok": True}


@app.get("/api/saved")
def api_get_saved():
    return db.get_saved()


@app.get("/api/health")
def health():
    return {"status": "ok"}

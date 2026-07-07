import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import db, claude_client
from app.claude_client import summarize_batch
from app.feeds import research, market, synthesis
from app.text_utils import strip_html, truncate

logger = logging.getLogger("niche.scheduler")

scheduler = AsyncIOScheduler()


def _passthrough_structure(items: list[dict]) -> list[dict]:
    """No-LLM fallback: use the raw title/description as-is so the feed still fills
    without an ANTHROPIC_API_KEY. No category, why-it-matters, or investor extraction."""
    structured = []
    for i, item in enumerate(items):
        structured.append(
            {
                "index": i,
                "headline": truncate(strip_html(item["title"]), 120),
                "summary": truncate(strip_html(item.get("raw_summary", "")), 280) or item["title"],
                "category": None,
                "why_it_matters": None,
                "mentioned_investors": [],
            }
        )
    return structured


async def _ingest_feed(fetch_fn, feed_name: str) -> int:
    raw_items = await fetch_fn()
    unseen = db.filter_unseen(raw_items)
    if not unseen:
        return 0

    if claude_client.is_configured():
        structured = summarize_batch(unseen, feed_name)
    else:
        structured = _passthrough_structure(unseen)
    by_index = {s["index"]: s for s in structured}

    inserted = 0
    for i, item in enumerate(unseen):
        s = by_index.get(i)
        if s is None:
            continue
        db.insert_summary(
            feed=feed_name,
            headline=s["headline"],
            summary=s["summary"],
            source_url=item["url"],
            source_label=item["source"],
            category=s.get("category"),
            image_url=item.get("image_url"),
            why_it_matters=s.get("why_it_matters"),
            mentioned_investors=s.get("mentioned_investors", []),
        )
        db.mark_seen(item["source"], item["url"])
        inserted += 1
    return inserted


async def hourly_job():
    from app.telegram_bot import notify

    try:
        research_count = await _ingest_feed(research.fetch_all, "research")
    except Exception:
        logger.exception("Feed 1 (research) ingest failed")
        research_count = 0

    try:
        market_count = await _ingest_feed(market.fetch_all, "market")
    except Exception:
        logger.exception("Feed 2 (market) ingest failed")
        market_count = 0

    if research_count or market_count:
        await notify(
            f"Hourly digest: {research_count} new research items, {market_count} new market items."
        )


async def daily_job():
    from app.telegram_bot import notify

    if not claude_client.is_configured():
        logger.info("Skipping daily synthesis — ANTHROPIC_API_KEY not set")
        return

    try:
        result = synthesis.run_daily_synthesis()
    except Exception:
        logger.exception("Feed 3 (synthesis) job failed")
        return

    if result is None:
        await notify("No niche idea generated today — not enough new items in the last 24h.")
        return

    await notify(f"Today's niche idea:\n\n{result['idea_text']}")


def start_scheduler():
    from datetime import datetime, timezone

    scheduler.add_job(
        hourly_job, "interval", hours=1, id="hourly_ingest", next_run_time=datetime.now(timezone.utc)
    )
    scheduler.add_job(daily_job, "cron", hour=8, minute=0, id="daily_synthesis")
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)

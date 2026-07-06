"""Feed 3 — Niche Ideas, once daily. Cross-references the last 24h of Feed 1 + Feed 2."""
from datetime import date
from typing import Optional

from app import db
from app.claude_client import synthesize_niche_idea


def run_daily_synthesis() -> Optional[dict]:
    research_summaries = db.get_summaries(feed="research", since_hours=24, limit=200)
    market_summaries = db.get_summaries(feed="market", since_hours=24, limit=200)

    result = synthesize_niche_idea(research_summaries, market_summaries)
    if result is None:
        return None

    today = date.today().isoformat()
    db.insert_niche_idea(today, result["idea_text"], result["source_refs"])
    return {"date": today, **result}

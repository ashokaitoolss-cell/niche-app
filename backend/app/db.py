import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from app.config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feed TEXT NOT NULL,
    category TEXT,
    headline TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_label TEXT NOT NULL,
    why_it_matters TEXT,
    mentioned_investors TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS niche_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    idea_text TEXT NOT NULL,
    source_refs TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_text TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_id INTEGER NOT NULL,
    saved_at TEXT NOT NULL,
    FOREIGN KEY (summary_id) REFERENCES summaries(id)
);

CREATE INDEX IF NOT EXISTS idx_summaries_feed_created ON summaries(feed, created_at);
CREATE INDEX IF NOT EXISTS idx_seen_items_url ON seen_items(url);
"""


def init_db():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_seen(url: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM seen_items WHERE url = ?", (url,)).fetchone()
        return row is not None


def mark_seen(source: str, url: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_items (source, url, fetched_at) VALUES (?, ?, ?)",
            (source, url, now_iso()),
        )


def filter_unseen(items: list[dict]) -> list[dict]:
    """Given raw items with a 'url' key, return only the ones not already in seen_items."""
    with get_conn() as conn:
        urls = [i["url"] for i in items]
        if not urls:
            return []
        placeholders = ",".join("?" * len(urls))
        rows = conn.execute(
            f"SELECT url FROM seen_items WHERE url IN ({placeholders})", urls
        ).fetchall()
        seen = {r["url"] for r in rows}
    return [i for i in items if i["url"] not in seen]


def insert_summary(
    feed: str,
    headline: str,
    summary: str,
    source_url: str,
    source_label: str,
    category: Optional[str] = None,
    why_it_matters: Optional[str] = None,
    mentioned_investors: Optional[list[str]] = None,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO summaries
               (feed, category, headline, summary, source_url, source_label,
                why_it_matters, mentioned_investors, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                feed,
                category,
                headline,
                summary,
                source_url,
                source_label,
                why_it_matters,
                json.dumps(mentioned_investors or []),
                now_iso(),
            ),
        )
        return cur.lastrowid


def get_summaries(feed: Optional[str] = None, since_hours: Optional[int] = None, limit: int = 50) -> list[dict]:
    query = "SELECT * FROM summaries"
    conditions = []
    params: list = []
    if feed:
        conditions.append("feed = ?")
        params.append(feed)
    if since_hours:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
        conditions.append("created_at >= ?")
        params.append(cutoff)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_investors(days: int = 30) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT mentioned_investors, created_at FROM summaries WHERE created_at >= ? AND feed = 'market'",
            (cutoff,),
        ).fetchall()
    counts: dict[str, int] = {}
    for row in rows:
        try:
            investors = json.loads(row["mentioned_investors"] or "[]")
        except json.JSONDecodeError:
            investors = []
        for name in investors:
            counts[name] = counts.get(name, 0) + 1
    return sorted(({"name": k, "mentions": v} for k, v in counts.items()), key=lambda x: -x["mentions"])


def insert_note(note_text: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes (note_text, created_at) VALUES (?, ?)", (note_text, now_iso())
        )
        return cur.lastrowid


def get_recent_notes(hours: int = 24) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notes WHERE created_at >= ? ORDER BY created_at DESC", (cutoff,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_niche_idea(date: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM niche_ideas WHERE date = ?", (date,)).fetchone()
        return dict(row) if row else None


def insert_niche_idea(date: str, idea_text: str, source_refs: list[int]) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO niche_ideas (date, idea_text, source_refs, created_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(date) DO UPDATE SET idea_text=excluded.idea_text,
                 source_refs=excluded.source_refs, created_at=excluded.created_at""",
            (date, idea_text, json.dumps(source_refs), now_iso()),
        )
        return cur.lastrowid


def save_summary(summary_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO saved (summary_id, saved_at) VALUES (?, ?)", (summary_id, now_iso())
        )
        return cur.lastrowid


def get_saved() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT s.*, sv.saved_at FROM saved sv
               JOIN summaries s ON s.id = sv.summary_id
               ORDER BY sv.saved_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]

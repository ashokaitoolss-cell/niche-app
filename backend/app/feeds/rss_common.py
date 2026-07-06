import feedparser
import httpx


async def fetch_rss(url: str, label: str) -> list[dict]:
    """Fetch and parse an RSS/Atom feed into a flat list of {title, url, summary, source} items."""
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "NicheDigestBot/1.0"})
        resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    items = []
    for entry in parsed.entries:
        link = entry.get("link")
        if not link:
            continue
        items.append(
            {
                "title": entry.get("title", "").strip(),
                "url": link,
                "raw_summary": entry.get("summary", "") or entry.get("description", ""),
                "source": label,
                "published": entry.get("published", ""),
            }
        )
    return items

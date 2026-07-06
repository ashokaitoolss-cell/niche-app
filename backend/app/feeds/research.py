"""Feed 1 — Research (AI / LLM / Semiconductors), hourly."""
import httpx

from app.feeds.rss_common import fetch_rss

ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.AR"]
ARXIV_API = "https://export.arxiv.org/api/query"

HN_ALGOLIA_API = "https://hn.algolia.com/api/v1/search_by_date"
HN_QUERY = "AI OR LLM OR semiconductor"

RESEARCH_RSS_FEEDS = [
    ("https://semianalysis.com/feed", "SemiAnalysis"),
    ("https://importai.substack.com/feed", "Import AI"),
    ("https://spectrum.ieee.org/feeds/topic/semiconductors.rss", "IEEE Spectrum"),
    ("https://techcrunch.com/category/artificial-intelligence/feed/", "TechCrunch AI"),
]


async def fetch_arxiv(hours: int = 2) -> list[dict]:
    """Pull recent arXiv submissions across the configured categories."""
    cat_query = " OR ".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    params = {
        "search_query": cat_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 30,
    }
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()

    import feedparser

    parsed = feedparser.parse(resp.content)
    items = []
    for entry in parsed.entries:
        items.append(
            {
                "title": entry.get("title", "").replace("\n", " ").strip(),
                "url": entry.get("id"),
                "raw_summary": entry.get("summary", "").replace("\n", " ").strip(),
                "source": "arXiv",
                "published": entry.get("published", ""),
            }
        )
    return items


async def fetch_hn(points_min: int = 20) -> list[dict]:
    params = {"query": HN_QUERY, "tags": "story", "numericFilters": f"points>{points_min}"}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(HN_ALGOLIA_API, params=params)
        resp.raise_for_status()
        data = resp.json()

    items = []
    for hit in data.get("hits", []):
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        items.append(
            {
                "title": hit.get("title", ""),
                "url": url,
                "raw_summary": hit.get("story_text") or "",
                "source": "Hacker News",
                "published": hit.get("created_at", ""),
                "points": hit.get("points", 0),
            }
        )
    return items


async def fetch_research_rss() -> list[dict]:
    all_items = []
    for url, label in RESEARCH_RSS_FEEDS:
        try:
            items = await fetch_rss(url, label)
            all_items.extend(items)
        except Exception:
            continue
    return all_items


async def fetch_all() -> list[dict]:
    arxiv_items = await fetch_arxiv()
    hn_items = await fetch_hn()
    rss_items = await fetch_research_rss()
    return arxiv_items + hn_items + rss_items

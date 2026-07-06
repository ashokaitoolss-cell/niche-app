"""Feed 2 — Consumer App Market Intel, hourly."""
import httpx

from app.config import PRODUCT_HUNT_TOKEN, CRUNCHBASE_API_KEY
from app.feeds.rss_common import fetch_rss

PRODUCT_HUNT_API = "https://api.producthunt.com/v2/api/graphql"

PRODUCT_HUNT_QUERY = """
query NewLaunches {
  posts(order: VOTES, postedAfter: "%s") {
    edges {
      node {
        id
        name
        tagline
        description
        url
        votesCount
        topics {
          edges { node { name } }
        }
      }
    }
  }
}
"""

MARKET_RSS_FEEDS = [
    ("https://techcrunch.com/tag/fundraise/feed/", "TechCrunch Fundraise"),
    ("https://www.lennysnewsletter.com/feed", "Lenny's Newsletter"),
    ("https://a16z.com/feed/", "a16z"),
    ("https://www.notboring.co/feed", "Not Boring"),
]

CRUNCHBASE_SEARCH_API = "https://api.crunchbase.com/api/v4/searches/organizations"
CONSUMER_CATEGORIES = {"consumer", "social", "dating"}


async def fetch_product_hunt(hours: int = 24) -> list[dict]:
    """New launches from Product Hunt, sorted by votes. Requires a developer token (v2 API)."""
    if not PRODUCT_HUNT_TOKEN:
        return []
    from datetime import datetime, timedelta, timezone

    posted_after = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = PRODUCT_HUNT_QUERY % posted_after
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.post(
            PRODUCT_HUNT_API,
            json={"query": query},
            headers={"Authorization": f"Bearer {PRODUCT_HUNT_TOKEN}"},
        )
        resp.raise_for_status()
        data = resp.json()

    items = []
    for edge in data.get("data", {}).get("posts", {}).get("edges", []):
        node = edge["node"]
        topics = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
        items.append(
            {
                "title": node.get("name", ""),
                "url": node.get("url"),
                "raw_summary": f"{node.get('tagline', '')}. {node.get('description', '')}".strip(),
                "source": "Product Hunt",
                "votes": node.get("votesCount", 0),
                "topics": topics,
            }
        )
    return items


async def fetch_crunchbase(days: int = 1) -> list[dict]:
    """Recent funding rounds in consumer/social/dating categories. Requires a Crunchbase API key."""
    if not CRUNCHBASE_API_KEY:
        return []
    payload = {
        "field_ids": ["identifier", "short_description", "categories", "website"],
        "query": [
            {
                "type": "predicate",
                "field_id": "categories",
                "operator_id": "includes",
                "values": list(CONSUMER_CATEGORIES),
            }
        ],
        "limit": 25,
    }
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.post(
            CRUNCHBASE_SEARCH_API,
            json=payload,
            headers={"X-cb-user-key": CRUNCHBASE_API_KEY},
        )
        resp.raise_for_status()
        data = resp.json()

    items = []
    for entity in data.get("entities", []):
        props = entity.get("properties", {})
        identifier = props.get("identifier", {})
        website = props.get("website", {}) or {}
        items.append(
            {
                "title": identifier.get("value", ""),
                "url": website.get("value") or f"https://www.crunchbase.com/organization/{identifier.get('permalink', '')}",
                "raw_summary": props.get("short_description", ""),
                "source": "Crunchbase",
            }
        )
    return items


async def fetch_market_rss() -> list[dict]:
    all_items = []
    for url, label in MARKET_RSS_FEEDS:
        try:
            items = await fetch_rss(url, label)
            all_items.extend(items)
        except Exception:
            continue
    return all_items


async def fetch_all() -> list[dict]:
    ph_items = await fetch_product_hunt()
    cb_items = await fetch_crunchbase()
    rss_items = await fetch_market_rss()
    return ph_items + cb_items + rss_items

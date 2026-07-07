import re
from typing import Optional

import feedparser
import httpx

_IMG_TAG_RE = re.compile(r'<img[^>]+src="([^"]+)"')


def _extract_image(entry) -> Optional[str]:
    media_thumbnail = entry.get("media_thumbnail")
    if media_thumbnail:
        url = media_thumbnail[0].get("url")
        if url:
            return url

    media_content = entry.get("media_content")
    if media_content:
        for m in media_content:
            if m.get("url"):
                return m["url"]

    for enc in entry.get("enclosures", []) or []:
        href = enc.get("href", "")
        if enc.get("type", "").startswith("image") or href.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            return href

    html_blob = entry.get("summary", "") or entry.get("description", "")
    if not html_blob and entry.get("content"):
        html_blob = entry["content"][0].get("value", "")
    match = _IMG_TAG_RE.search(html_blob)
    if match:
        return match.group(1)

    return None


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
                "image_url": _extract_image(entry),
            }
        )
    return items

import json
from typing import Optional

from anthropic import Anthropic

from app.config import ANTHROPIC_API_KEY, CLAUDE_MODEL

_client: Optional[Anthropic] = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        _client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


SUMMARIZE_TOOL = {
    "name": "record_summaries",
    "description": "Record structured summaries for a batch of raw feed items.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summaries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer", "description": "index of the source item in the input list"},
                        "headline": {"type": "string", "description": "sharp, specific headline, under 15 words"},
                        "summary": {"type": "string", "description": "2-3 sentence plain summary"},
                        "category": {"type": "string", "description": "short category label, e.g. 'funding', 'model release', 'infra'"},
                        "why_it_matters": {"type": "string", "description": "one sentence on why this is significant"},
                        "mentioned_investors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "any VC firms or angel investors named in the item, empty if none",
                        },
                    },
                    "required": ["index", "headline", "summary", "category", "why_it_matters", "mentioned_investors"],
                },
            }
        },
        "required": ["summaries"],
    },
}

SYNTHESIZE_TOOL = {
    "name": "record_niche_idea",
    "description": "Record the single daily synthesis idea.",
    "input_schema": {
        "type": "object",
        "properties": {
            "idea_text": {
                "type": "string",
                "description": "one buildable, narrow, solo-shippable product concept: the specific pain point or funding gap, the concrete feature, and the target user",
            },
            "source_indices": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "indices into the provided source list that informed this idea",
            },
        },
        "required": ["idea_text", "source_indices"],
    },
}


def summarize_batch(items: list[dict], feed: str) -> list[dict]:
    """Send raw items to Claude for categorization + summarization. Returns list aligned by 'index'."""
    if not items:
        return []

    numbered = "\n\n".join(
        f"[{i}] title: {it['title']}\nsource: {it['source']}\nraw: {it.get('raw_summary', '')[:800]}"
        for i, it in enumerate(items)
    )
    feed_context = (
        "AI/LLM/semiconductor research items from arXiv, Hacker News, and industry RSS."
        if feed == "research"
        else "consumer app market intel items: funding rounds, launches, and operator/investor commentary."
    )

    client = get_client()
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        tools=[SUMMARIZE_TOOL],
        tool_choice={"type": "tool", "name": "record_summaries"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"Summarize and categorize each of these {feed_context}\n\n"
                    f"{numbered}\n\n"
                    "Call record_summaries with one entry per item, in the same order."
                ),
            }
        ],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "record_summaries":
            return block.input.get("summaries", [])
    return []


def synthesize_niche_idea(research_summaries: list[dict], market_summaries: list[dict]) -> Optional[dict]:
    """Cross-reference the last 24h of both feeds into one buildable idea."""
    if not research_summaries and not market_summaries:
        return None

    combined = research_summaries + market_summaries
    offset = len(research_summaries)
    listing = "\n".join(
        f"[{i}] ({'research' if i < offset else 'market'}) {s['headline']}: {s['summary']}"
        for i, s in enumerate(combined)
    )

    client = get_client()
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        tools=[SYNTHESIZE_TOOL],
        tool_choice={"type": "tool", "name": "record_niche_idea"},
        messages=[
            {
                "role": "user",
                "content": (
                    "Here are the last 24 hours of research (AI/LLM/semiconductor) and consumer app "
                    "market intel items:\n\n"
                    f"{listing}\n\n"
                    "Find exactly ONE overlap: either (a) a pain point from the research items that has "
                    "no consumer product addressing it in the market items, or (b) a funding gap in the "
                    "market items — a category VCs are avoiding or a vertical nobody is building in — that "
                    "a technical solo builder could fill.\n\n"
                    "Reject generic 'AI-powered X' answers. The idea must name a concrete feature and a "
                    "specific target user, and must be narrow enough for one person to ship. "
                    "Call record_niche_idea with your answer and the source indices that informed it."
                ),
            }
        ],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "record_niche_idea":
            data = block.input
            source_refs = [
                combined[i]["id"] for i in data.get("source_indices", []) if i < len(combined) and "id" in combined[i]
            ]
            return {"idea_text": data["idea_text"], "source_refs": source_refs}
    return None

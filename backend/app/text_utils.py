import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    text = _TAG_RE.sub(" ", text or "")
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def truncate(text: str, length: int) -> str:
    text = text.strip()
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"

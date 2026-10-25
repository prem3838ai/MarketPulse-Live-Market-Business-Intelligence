from __future__ import annotations
from datetime import datetime, timezone
import requests

POSITIVE = {"growth", "gain", "gains", "profit", "profits", "record", "surge", "surges", "strong", "beat", "beats", "upgrade", "positive", "rise", "rises", "improve", "improved", "success", "deal", "launch"}
NEGATIVE = {"loss", "losses", "decline", "declines", "fall", "falls", "drop", "drops", "weak", "miss", "misses", "downgrade", "negative", "risk", "risks", "lawsuit", "cut", "cuts", "crisis", "warning", "warns"}


def lexicon_sentiment(text: str) -> float:
    words = [w.strip(".,!?():;\"'[]{}") .lower() for w in (text or "").split()]
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    total = pos + neg
    return round((pos - neg) / total, 3) if total else 0.0


def fetch_news(query: str, limit: int = 20, timeout: int = 15) -> list[dict]:
    query = query.strip()
    if not query:
        raise ValueError("Enter a company, ticker, or topic to search news.")
    limit = max(1, min(int(limit), 50))
    endpoint = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {"query": query, "mode": "ArtList", "format": "json", "sort": "DateDesc", "maxrecords": limit}
    try:
        response = requests.get(endpoint, params=params, timeout=timeout, headers={"User-Agent": "MarketPulsePortfolio/1.0"})
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError(f"Live news service unavailable: {exc}") from exc
    articles = payload.get("articles", []) if isinstance(payload, dict) else []
    rows = []
    for item in articles[:limit]:
        title = str(item.get("title") or "Untitled article")
        rows.append({
            "title": title,
            "url": str(item.get("url") or ""),
            "source": str(item.get("domain") or item.get("sourceCountry") or "Unknown"),
            "published_at": str(item.get("seendate") or ""),
            "sentiment": lexicon_sentiment(title),
        })
    return rows

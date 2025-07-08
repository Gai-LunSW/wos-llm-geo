from __future__ import annotations

from typing import Iterable, List, Dict, Any
import pandas as pd

# Simple in-memory cache for geocoding results
_GEOCODE_CACHE: Dict[str, Dict[str, float]] = {}


def analyze_articles_batch(articles: Iterable[str]) -> pd.DataFrame:
    """Return analysis results for a batch of article texts.

    Each article is summarized with a dummy implementation. The function
    returns a DataFrame with two columns: ``article`` and ``summary``.
    """
    summaries: List[Dict[str, Any]] = []
    for article in articles:
        summary = f"summary for {article[:10]}"
        summaries.append({"article": article, "summary": summary})
    return pd.DataFrame(summaries)


def _geocode_location(location: str) -> Dict[str, float]:
    """Dummy geocode a single location."""
    # In real code this would call an external service.
    return {"lat": hash(location) % 90, "lng": hash(location[::-1]) % 180}


def geocode_locations(locations: Iterable[str]) -> pd.DataFrame:
    """Geocode a list of location strings with caching."""
    results: List[Dict[str, Any]] = []
    for loc in locations:
        if loc in _GEOCODE_CACHE:
            coords = _GEOCODE_CACHE[loc]
        else:
            coords = _geocode_location(loc)
            _GEOCODE_CACHE[loc] = coords
        results.append({"location": loc, **coords})
    return pd.DataFrame(results)


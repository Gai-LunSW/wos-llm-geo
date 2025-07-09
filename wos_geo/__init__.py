from __future__ import annotations

from typing import Iterable, List, Dict, Any, Optional, Sequence
import pandas as pd

# Simple in-memory cache for geocoding results
_GEOCODE_CACHE: Dict[str, Dict[str, float]] = {}


def analyze_articles_batch(
    articles: Iterable[str],
    *,
    prompt_template: str | None = None,
) -> pd.DataFrame:
    """Return analysis results for a batch of article texts.

    Parameters
    ----------
    articles:
        Iterable of article texts to analyze.
    prompt_template:
        Optional template used to build the summary for each article.  ``{text}``
        within the template is replaced with the article text.  If omitted a
        simple placeholder summary is generated.

    Returns
    -------
    pandas.DataFrame
        Data frame containing at least ``article`` and ``summary`` columns.
    """

    if prompt_template is None:
        prompt_template = "summary for {text}"  # dummy placeholder

    summaries: List[Dict[str, Any]] = []
    for article in articles:
        summary = prompt_template.format(text=article)
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


def analyze_articles_to_excel(
    articles: Iterable[str],
    output_path: str,
    *,
    prompt_template: str | None = None,
    columns: Optional[Sequence[str]] = None,
) -> str:
    """Analyze ``articles`` and save the result to an Excel file.

    Parameters
    ----------
    articles:
        Articles to summarize.
    output_path:
        File path where the Excel file should be written.
    prompt_template:
        Optional template passed to :func:`analyze_articles_batch`.
    columns:
        If provided, subset of dataframe columns to include in the Excel file.

    Returns
    -------
    str
        The ``output_path`` argument, for convenience.
    """

    df = analyze_articles_batch(articles, prompt_template=prompt_template)
    if columns is not None:
        df = df[list(columns)]
    df.to_excel(output_path, index=False)
    return output_path


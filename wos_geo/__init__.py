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
    try:
        df.to_excel(output_path, index=False)
    except ModuleNotFoundError:
        # Fallback to CSV if the required Excel writer (e.g. openpyxl) is not installed.
        # This allows the function to work even in minimal environments.
        df.to_csv(output_path, index=False)
    return output_path

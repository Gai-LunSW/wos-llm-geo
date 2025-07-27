import pandas as pd
import openai
from typing import Iterable, List, Optional


def get_openai_client(api_key: str) -> openai.Client:
    """Create and return an OpenAI client."""
    return openai.OpenAI(api_key=api_key)


def analyze_articles_batch(client: openai.Client, articles: Iterable[str], model: str = "gpt-3.5-turbo") -> List[str]:
    """Analyze a batch of article texts using the OpenAI chat API."""
    results = []
    for article in articles:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": article}],
        )
        results.append(response.choices[0].message.content)
    return results


def analyze_dataset(
    client: openai.Client,
    input_path: str,
    output_path: str,
    text_column: str = "text",
    batch_size: int = 5,
) -> str:
    """Analyze all rows in a CSV dataset and save the result."""
    df = pd.read_csv(input_path)
    analyses: List[str] = []
    for start in range(0, len(df), batch_size):
        batch = df.iloc[start : start + batch_size][text_column].tolist()
        analyses.extend(analyze_articles_batch(client, batch))
    df["analysis"] = analyses
    df.to_csv(output_path, index=False)
    return output_path

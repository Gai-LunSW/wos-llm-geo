#!/usr/bin/env python
"""
Combined script for analyzing WoS articles to extract research region and country
using OpenAI and geocoding the results with Google Maps.
"""

import os
import logging
import time
import argparse
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import httpx
from httpx import Limits, Timeout
import googlemaps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env if present
load_dotenv()

def get_openai_client(api_key: str) -> OpenAI:
    http_client = httpx.Client(
        limits=Limits(max_connections=10, max_keepalive_connections=5),
        timeout=Timeout(10.0, read=10.0, write=10.0, connect=10.0),
    )
    return OpenAI(api_key=api_key, max_retries=5, http_client=http_client)

# Initialize tokenizer for GPT-4o-mini
encoding = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def analyze_articles_batch(client: OpenAI, batch: list, max_retries: int = 10) -> list[str]:
    """
    Send a batch of articles to the OpenAI API and return the extracted
    region and country strings.
    """
    prompt_base = (
        "根据以下摘要和题目，提取总结以下信息：\n"
        "研究区名称(英语)\n"
        "国家名称(英语,如有多个国家只生成一个)\n"
        "没有匹配成功就输出null。请注意：每次处理25份数据并已分点标记。输出时结果和输入必须一一对应。\n"
    )
    prompt_end = "请按照以下格式输出结果：\n英文研究区A，英文国家A\n"

    numbered_articles = []
    for i, article in enumerate(batch):
        title = article["Article Title"]
        abstract = article["Abstract"]
        numbered_articles.append(f"{i+1}. 题目: {title}\n摘要: {abstract}\n")

    prompt = prompt_base + "\n".join(numbered_articles) + "\n" + prompt_end

    backoff_time = 5
    retries = 0

    while retries < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是地理学方面的专家。你对国家和国家下行政区非常敏感，以及对流域，海洋，河流的具体名称非常敏感。"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3000,
            )
            result = response.choices[0].message.content.strip()
            return [line.strip() for line in result.splitlines() if line.strip()]
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 504):
                retries += 1
                logger.warning(
                    "Error %s. Retrying in %s seconds... (Attempt %s/%s)",
                    e.response.status_code,
                    backoff_time,
                    retries,
                    max_retries,
                )
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, 120)
            else:
                logger.error("HTTP error: %s", e.response.status_code)
                break
        except Exception as e:
            retries += 1
            logger.error(
                "Unexpected error: %s. Retrying in %s seconds... (Attempt %s/%s)",
                e,
                backoff_time,
                retries,
                max_retries,
            )
            time.sleep(backoff_time)
    raise RuntimeError(f"Failed to analyze articles after {max_retries} attempts")

def analyze_dataset(
    df: pd.DataFrame,
    client: OpenAI,
    start_index: int,
    batch_size: int,
) -> pd.DataFrame:
    """Iterate over the dataframe and fill the 'Analyzed Result' column."""
    df = df.copy()
    df["Analyzed Result"] = df.get("Analyzed Result", "")

    for start in tqdm(range(start_index, df.shape[0], batch_size), desc="LLM analysis"):
        batch = df.iloc[start : start + batch_size].to_dict("records")
        try:
            results = analyze_articles_batch(client, batch)
            for i, res in enumerate(results):
                df.at[start + i, "Analyzed Result"] = res
        except Exception as e:
            logger.error("Error processing batch starting at index %s: %s", start, e)
            break
    return df

def geocode_locations(
    df: pd.DataFrame, gmaps: googlemaps.Client, batch_size: int = 100
) -> pd.DataFrame:
    """
    Geocode the locations in the 'Analyzed Result' column.
    A simple in-memory cache is used to avoid duplicate API calls.
    """
    df = df.copy()
    latitudes: list[float | None] = []
    longitudes: list[float | None] = []
    cache: dict[str, tuple[float | None, float | None]] = {}

    for i in tqdm(range(0, len(df), batch_size), desc="Geocoding"):
        batch_df = df.iloc[i : i + batch_size]
        for location in batch_df["Analyzed Result"]:
            if location == "无":
                lat, lng = None, None
            else:
                if location in cache:
                    lat, lng = cache[location]
                else:
                    try:
                        geocode_result = gmaps.geocode(location)
                        if geocode_result:
                            loc = geocode_result[0]["geometry"]["location"]
                            lat, lng = loc["lat"], loc["lng"]
                        else:
                            lat, lng = None, None
                    except Exception as e:
                        logger.error("Error fetching coordinates for %s: %s", location, e)
                        lat, lng = None, None
                    cache[location] = (lat, lng)
            latitudes.append(lat)
            longitudes.append(lng)

    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    return df

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze WoS data and geocode locations")
    parser.add_argument("--input", required=True, help="Path to the input Excel file")
    parser.add_argument(
        "--output",
        default="processed_data.xlsx",
        help="Path to save the final Excel file",
    )
    parser.add_argument("--start-index", type=int, default=0, help="Row index to start processing")
    parser.add_argument("--llm-batch-size", type=int, default=25, help="Batch size for LLM requests")
    parser.add_argument("--geo-batch-size", type=int, default=100, help="Batch size for geocoding")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    # Prepare OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing")
    openai_client = get_openai_client(api_key)

    # Prepare Google Maps client
    gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not gmaps_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is missing")
    gmaps_client = googlemaps.Client(key=gmaps_key)

    df = pd.read_excel(args.input)

    # Analyse articles with LLM
    df = analyze_dataset(df, openai_client, args.start_index, args.llm_batch_size)

    # Geocode the results
    df = geocode_locations(df, gmaps_client, batch_size=args.geo_batch_size)

    df.to_excel(args.output, index=False)
    logger.info("Processing complete. Results saved to: %s", args.output)

if __name__ == "__main__":
    main()

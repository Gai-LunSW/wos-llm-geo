import argparse
import os
import pandas as pd
from tqdm import tqdm

try:
    import openai
except ImportError:  # placeholder if openai not installed
    openai = None

try:
    import googlemaps
except ImportError:
    googlemaps = None


def analyze_dataset(input_path: str, output_path: str, *,
                     checkpoint_path: str | None = None,
                     checkpoint_interval: int = 10,
                     batch_size: int = 10) -> pd.DataFrame:
    """Analyze dataset using LLM and support checkpointing."""
    if checkpoint_path and os.path.exists(checkpoint_path):
        df = pd.read_csv(checkpoint_path)
    else:
        df = pd.read_csv(input_path)
        if "analysis_result" not in df.columns:
            df["analysis_result"] = pd.NA
    start_idx = df[df["analysis_result"].isna()].index.min()
    if pd.isna(start_idx):
        return df

    for i in tqdm(range(start_idx, len(df), batch_size)):
        batch = df.iloc[i:i + batch_size]
        for idx, row in batch.iterrows():
            text = str(row.get("text", ""))
            result = ""
            if openai is not None:
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": text}]
                    )
                    result = resp.choices[0].message.content.strip()
                except Exception as exc:  # pragma: no cover - external service
                    result = str(exc)
            df.at[idx, "analysis_result"] = result
        if checkpoint_path and ((i // batch_size + 1) % checkpoint_interval == 0):
            df.to_csv(checkpoint_path, index=False)
    df.to_csv(output_path, index=False)
    if checkpoint_path:
        df.to_csv(checkpoint_path, index=False)
    return df


def geocode_locations(input_path: str, output_path: str, *,
                      checkpoint_path: str | None = None,
                      checkpoint_interval: int = 10,
                      batch_size: int = 10,
                      api_key: str | None = None) -> pd.DataFrame:
    """Geocode addresses with checkpointing."""
    if checkpoint_path and os.path.exists(checkpoint_path):
        df = pd.read_csv(checkpoint_path)
    else:
        df = pd.read_csv(input_path)
        if "lat" not in df.columns:
            df["lat"] = pd.NA
        if "lng" not in df.columns:
            df["lng"] = pd.NA
    start_idx = df[df["lat"].isna() | df["lng"].isna()].index.min()
    if pd.isna(start_idx):
        return df
    client = googlemaps.Client(key=api_key) if googlemaps is not None and api_key else None
    for i in tqdm(range(start_idx, len(df), batch_size)):
        batch = df.iloc[i:i + batch_size]
        for idx, row in batch.iterrows():
            address = str(row.get("address", ""))
            lat, lng = None, None
            if client:
                try:
                    geocode_result = client.geocode(address)
                    if geocode_result:
                        location = geocode_result[0]["geometry"]["location"]
                        lat, lng = location["lat"], location["lng"]
                except Exception as exc:  # pragma: no cover - external service
                    lat, lng = str(exc), str(exc)
            df.at[idx, "lat"] = lat
            df.at[idx, "lng"] = lng
        if checkpoint_path and ((i // batch_size + 1) % checkpoint_interval == 0):
            df.to_csv(checkpoint_path, index=False)
    df.to_csv(output_path, index=False)
    if checkpoint_path:
        df.to_csv(checkpoint_path, index=False)
    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WoS LLM geolocation utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_analyze = subparsers.add_parser("analyze", help="run LLM analysis")
    parser_analyze.add_argument("--input", required=True, help="Input CSV file")
    parser_analyze.add_argument("--output", required=True, help="Output CSV file")
    parser_analyze.add_argument("--checkpoint", help="Checkpoint CSV file")
    parser_analyze.add_argument("--checkpoint-interval", type=int, default=10,
                               help="Save checkpoint every N batches")
    parser_analyze.add_argument("--batch-size", type=int, default=10)

    parser_geocode = subparsers.add_parser("geocode", help="geocode addresses")
    parser_geocode.add_argument("--input", required=True, help="Input CSV file")
    parser_geocode.add_argument("--output", required=True, help="Output CSV file")
    parser_geocode.add_argument("--checkpoint", help="Checkpoint CSV file")
    parser_geocode.add_argument("--checkpoint-interval", type=int, default=10,
                               help="Save checkpoint every N batches")
    parser_geocode.add_argument("--batch-size", type=int, default=10)
    parser_geocode.add_argument("--api-key", help="Google Maps API key")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "analyze":
        analyze_dataset(
            args.input,
            args.output,
            checkpoint_path=args.checkpoint,
            checkpoint_interval=args.checkpoint_interval,
            batch_size=args.batch_size,
        )
    elif args.command == "geocode":
        geocode_locations(
            args.input,
            args.output,
            checkpoint_path=args.checkpoint,
            checkpoint_interval=args.checkpoint_interval,
            batch_size=args.batch_size,
            api_key=args.api_key,
        )


if __name__ == "__main__":
    main()

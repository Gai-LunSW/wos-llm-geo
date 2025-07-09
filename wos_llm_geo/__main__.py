import argparse

from .analysis import get_openai_client, analyze_dataset
from .geocode import geocode_locations


def main():
    parser = argparse.ArgumentParser(description="Analyze WoS data and geocode locations")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--openai-key", required=True, help="OpenAI API key")
    parser.add_argument("--output", required=True, help="Output CSV for analysis results")
    parser.add_argument("--gmaps-key", help="Google Maps API key for geocoding")
    parser.add_argument(
        "--text-column",
        default="text",
        help="CSV column containing article text (default: text)",
    )
    args = parser.parse_args()

    client = get_openai_client(args.openai_key)
    analyzed_path = analyze_dataset(client, args.input, args.output, text_column=args.text_column)

    if args.gmaps_key:
        geocode_locations(analyzed_path, args.gmaps_key)


if __name__ == "__main__":
    main()

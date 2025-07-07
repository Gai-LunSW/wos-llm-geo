# wos-llm-geo

This repository provides tools to extract research regions from Web of Science (WoS) records using OpenAI models and then geocode those locations with Google Maps.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Set the following environment variables with your API keys:

- `OPENAI_API_KEY`
- `GOOGLE_MAPS_API_KEY`

You can place them in a `.env` file as well.

## Usage

Run the combined processing script:

```bash
python wos_llm_geo.py --input path/to/combined_data.xlsx --output processed_data.xlsx
```

Optional arguments allow configuring the start index and batch sizes for both the LLM analysis and geocoding steps.

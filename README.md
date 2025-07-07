# wos-llm-geo

Extract region and geolocation from WoS data using LLMs + Google Maps API.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the CLI:

```bash
python -m wos_llm_geo --input data.csv --openai-key YOUR_OPENAI_KEY --output results.csv --gmaps-key YOUR_GMAPS_KEY
```

The command reads `data.csv`, analyzes it with OpenAI and optionally geocodes the locations using Google Maps if a key is provided.

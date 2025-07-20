# wos-llm-geo

Extract region and geolocation from WoS data using LLMs and the Google Maps API.

## Installation

```bash
pip install -r requirements.txt
```

This installs both the runtime dependencies and the testing tools (`pytest` and `pytest-cov`).

## Configuration

The library expects the following environment variables to be defined:

- `OPENAI_API_KEY` – API key for OpenAI services
- `GOOGLE_MAPS_API_KEY` – Google Maps API key

A convenient way to set them is by creating a `.env` file in the project root. Values
in this file will be loaded automatically if present.

## Usage

Use `wos_geo.analyze_articles_batch` to obtain a DataFrame of article
summaries. The function accepts an optional `prompt_template` parameter
allowing you to customise how each summary is generated.

Results can be written directly to an Excel file with
`wos_geo.analyze_articles_to_excel` which returns the path to the saved file.

## Running Tests

Before running the tests make sure `pytest` and `pytest-cov` are installed. If you
installed the requirements with `pip install -r requirements.txt` then both
packages will already be available.

Execute the test suite with coverage using:

```bash
pip install -r requirements.txt && pytest
```

A coverage report will be shown after the tests complete.

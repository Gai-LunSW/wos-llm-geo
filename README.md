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

## Running Tests

Execute the test suite with coverage information using:

```bash
pytest
```

A coverage report will be shown after the tests complete.

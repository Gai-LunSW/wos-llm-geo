# wos-llm-geo
Extract region and geolocation from WoS data using LLMs + Google Maps API

## Usage

The project provides a CLI implemented in `wos_geo.py` with two sub-commands:

- `analyze`: run the LLM on each record
- `geocode`: resolve addresses using the Google Maps API

Both commands accept a `--checkpoint` path and `--checkpoint-interval` option.
When provided, the script periodically saves the processed `DataFrame` to this
CSV file so that execution can resume from the last written state if restarted.

Example:

```bash
python wos_geo.py analyze --input data.csv --output analyzed.csv \
  --checkpoint tmp/analyze_checkpoint.csv --checkpoint-interval 5 --batch-size 20

python wos_geo.py geocode --input analyzed.csv --output geocoded.csv \
  --checkpoint tmp/geocode_checkpoint.csv --checkpoint-interval 5 --batch-size 20 \
  --api-key YOUR_GMAPS_KEY
```

If the checkpoint file exists on startup, it will be loaded and processing will
continue from the first unprocessed row.

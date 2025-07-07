# wos-llm-geo
Extract region and geolocation from WoS data using LLMs + Google Maps API

## Configuration

The application uses a YAML configuration file. A sample `config.yaml` is
included in the repository:

```yaml
start_index: 0
llm_batch_size: 20
geo_batch_size: 10
```

Create your own file or modify these values as needed. Pass the path to your
custom configuration with the `--config` option:

## Usage

Run the main script and optionally specify a configuration file or override
individual options from the command line:

```bash
python main.py --config myconfig.yaml --llm-batch-size 5
```

Command line arguments take precedence over the values in the YAML file.

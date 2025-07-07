import argparse
import os
import yaml


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Process WoS data with LLM and geocoding')
    parser.add_argument('--config', default='config.yaml', help='Path to YAML config file')
    parser.add_argument('--start-index', type=int, help='Override start index from config')
    parser.add_argument('--llm-batch-size', type=int, help='Override LLM batch size from config')
    parser.add_argument('--geo-batch-size', type=int, help='Override geolocation batch size from config')
    return parser.parse_args()


def merge_config(args: argparse.Namespace, config: dict) -> dict:
    merged = config.copy()
    if args.start_index is not None:
        merged['start_index'] = args.start_index
    if args.llm_batch_size is not None:
        merged['llm_batch_size'] = args.llm_batch_size
    if args.geo_batch_size is not None:
        merged['geo_batch_size'] = args.geo_batch_size
    return merged


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    config = merge_config(args, config)
    print('Final configuration:')
    for k, v in config.items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()

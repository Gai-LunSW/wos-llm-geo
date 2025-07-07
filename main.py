"""Main application entry point for WoS LLM geolocation extraction."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml


@dataclass
class Config:
    """Application configuration."""

    start_index: int = 0
    llm_batch_size: int = 20
    geo_batch_size: int = 10

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create a configuration instance from a dictionary."""
        return cls(
            start_index=data.get("start_index", cls.start_index),
            llm_batch_size=data.get("llm_batch_size", cls.llm_batch_size),
            geo_batch_size=data.get("geo_batch_size", cls.geo_batch_size),
        )


def load_config(path: str) -> Config:
    """Load configuration from a YAML file."""
    if not os.path.exists(path):
        return Config()
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Config.from_dict(data)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process WoS data with LLM and geocoding"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        help="Override start index from config",
    )
    parser.add_argument(
        "--llm-batch-size",
        type=int,
        help="Override LLM batch size from config",
    )
    parser.add_argument(
        "--geo-batch-size",
        type=int,
        help="Override geolocation batch size from config",
    )
    return parser.parse_args()


def merge_config(args: argparse.Namespace, config: Config) -> Config:
    """Merge command line arguments into a configuration instance."""
    if args.start_index is not None:
        config.start_index = args.start_index
    if args.llm_batch_size is not None:
        config.llm_batch_size = args.llm_batch_size
    if args.geo_batch_size is not None:
        config.geo_batch_size = args.geo_batch_size
    return config


def main() -> None:
    """Script entry point."""
    args = parse_args()
    config = load_config(args.config)
    config = merge_config(args, config)

    print("Final configuration:")
    print(f"start_index: {config.start_index}")
    print(f"llm_batch_size: {config.llm_batch_size}")
    print(f"geo_batch_size: {config.geo_batch_size}")


if __name__ == '__main__':
    main()

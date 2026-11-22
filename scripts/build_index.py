"""Build Chroma index from CloudServe documentation.json (real corpus)."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.retrieve import build_index, reset_retrieve_cache


def main() -> None:
    parser = argparse.ArgumentParser(description="Index CloudServe documentation corpus")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to documentation.json from datasets directory (05_Datasets)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        default=True,
        help="Delete existing collection before indexing (default true)",
    )
    args = parser.parse_args()
    reset_retrieve_cache()
    n = build_index(Path(args.input), reset=args.reset)
    print(f"indexed_chunks={n}")


if __name__ == "__main__":
    main()

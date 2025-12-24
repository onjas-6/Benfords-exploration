#!/usr/bin/env python3
"""
Main analysis script for Benford's Law validation.
"""

import sys
from pathlib import Path
import argparse

from src.analyzer import analyze


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Wikipedia numbers for Benford's Law validation"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/numbers.parquet"),
        help="Path to numbers.parquet file (default: data/numbers.parquet)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output directory for plots and stats (default: output)"
    )
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not args.data.exists():
        print(f"Error: Data file not found: {args.data}", file=sys.stderr)
        print("Run process_wiki.py first to generate the data.", file=sys.stderr)
        return 1
    
    # Run analysis
    try:
        analyze(args.data, args.output)
        return 0
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


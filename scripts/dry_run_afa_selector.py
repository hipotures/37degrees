#!/usr/bin/env python3
"""
Dry-run AFA selector using updated balancing and guardrails.

Reads a small set of books with existing afa_analysis.scores, recomputes
DEPTH/HEAT and selects a format using select_format_from_matrix().

Does NOT modify any book files. Uses a temporary distribution file under output/.

Usage:
  python scripts/dry_run_afa_selector.py [book_folder ...]

If no folders are given, a default sample is used.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import yaml

sys.path.append('./scripts/lib')
from afa_calculations import calculate_depth_heat_composites, select_format_from_matrix


DEFAULT_BOOKS = [
    "books/0012_harry_potter",
    "books/0020_narnia",
    "books/0019_master_and_margarita",
    "books/0037_wuthering_heights",
    "books/0009_fahrenheit_451",
]


def load_scores(book_yaml_path: Path) -> Dict[str, Any] | None:
    data = yaml.safe_load(book_yaml_path.read_text(encoding="utf-8"))
    scores = data.get("afa_analysis", {}).get("scores")
    if not scores:
        return None
    # build ai_response-like structure
    return {
        'raw_scores': {
            k: {'value': v} for k, v in scores.items()
            if k not in ("total", "percentile")
        }
    }


def old_format_name(book_yaml_path: Path) -> str | None:
    data = yaml.safe_load(book_yaml_path.read_text(encoding="utf-8"))
    fmts = data.get("afa_analysis", {}).get("formats")
    if not fmts:
        return None
    return list(fmts.keys())[0]


def main(argv: List[str]) -> int:
    books = argv[1:] if len(argv) > 1 else DEFAULT_BOOKS
    dist_path = Path("output/afa_format_counts_dryrun.json")

    print("== AFA Selector Dry-Run ==")
    print(f"Using distribution file: {dist_path}")

    changed = 0
    checked = 0

    for folder in books:
        book_dir = Path(folder)
        book_yaml = book_dir / "book.yaml"
        if not book_yaml.exists():
            print(f"- Skipping {folder} (no book.yaml)")
            continue

        ai_response = load_scores(book_yaml)
        if not ai_response:
            print(f"- Skipping {folder} (no afa_analysis.scores)")
            continue

        # Compute composites
        DEPTH, depth_cat, HEAT, heat_cat = calculate_depth_heat_composites(ai_response)

        # Select with updated logic, using a dry-run distribution file
        selected = select_format_from_matrix(
            depth_cat, heat_cat, ai_response=ai_response, distribution_file=str(dist_path)
        )

        prev = old_format_name(book_yaml)
        checked += 1
        changed_flag = "(same)"
        if prev and prev != selected["name"]:
            changed += 1
            changed_flag = "(CHANGED)"

        title = yaml.safe_load(book_yaml.read_text(encoding="utf-8")).get("book_info", {}).get("title", book_dir.name)

        print(
            f"- {book_dir.name}: {title}\n"
            f"  DEPTH {DEPTH:.1f} [{depth_cat}] | HEAT {HEAT:.1f} [{heat_cat}]\n"
            f"  old: {prev or 'None'}  ->  new: {selected['name']} ({selected['duration']}m) {changed_flag}\n"
        )

    print(f"Summary: {changed} changed out of {checked} checked.")
    print("Note: Dry-run used a separate distribution file and did not modify books.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


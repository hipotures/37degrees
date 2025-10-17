#!/usr/bin/env python3
"""
Scan audio directories and report books missing language tracks.

By default the script inspects both ``books/`` and ``media/`` subdirectories.
Each book is expected to have exactly the 9 language files
(``de, en, es, fr, hi, ja, ko, pl, pt``) inside its ``audio/`` folder.  Files
must be larger than 1 MB to qualify.  Extra files are ignored as long as the
required set is complete.

Examples
--------
    # Check both books/ and media/
    python scripts/check_audio_language_completeness.py

    # Only check books/
    python scripts/check_audio_language_completeness.py --books

    # Only check media/ and show empty audio directories
    python scripts/check_audio_language_completeness.py --media --show-empty
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess

SUPPORTED_LANG_CODES = ["de", "en", "es", "fr", "hi", "ja", "ko", "pl", "pt"]
ALLOWED_EXTENSIONS = {".mp3", ".m4a", ".mp4", ".wav"}
DEFAULT_MIN_SIZE_MB = 1.0
TODO_LIST_KEY = "cc-au-notebooklm"

def find_language_files(audio_dir: Path, book_slug: str, languages: List[str], min_bytes: int) -> Dict[str, Tuple[Path, int]]:
    language_files: Dict[str, Tuple[Path, int]] = {}
    if not audio_dir.exists():
        return language_files
    for child in audio_dir.iterdir():
        if not child.is_file():
            continue
        suffix = child.suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            continue
        name_without_suffix = child.name[: -len(suffix)]
        if not name_without_suffix.startswith(f"{book_slug}_"):
            continue
        lang = name_without_suffix.split("_")[-1]
        if lang not in languages:
            continue
        size = child.stat().st_size
        if size < min_bytes:
            language_files.setdefault(lang, (child, size))
            continue
        current = language_files.get(lang)
        if current is None or size > current[1]:
            language_files[lang] = (child, size)
    return language_files

def inspect_base_directory(base_dir: Path, languages: List[str], min_bytes: int, show_empty: bool) -> Tuple[List[str], List[str], Dict[Path, List[str]]]:
    missing_reports: List[str] = []
    empty_reports: List[str] = []
    missing_map: Dict[Path, List[str]] = {}
    if not base_dir.exists():
        return missing_reports, empty_reports, missing_map

    for book_dir in sorted(p for p in base_dir.iterdir() if p.is_dir()):
        audio_dir = book_dir / "audio"
        if not audio_dir.exists():
            if show_empty:
                empty_reports.append(f"{book_dir.resolve().relative_to(Path.cwd()) if audio_dir.exists() else book_dir}")
            continue

        files_in_audio = [p for p in audio_dir.iterdir() if p.is_file()]
        if not files_in_audio:
            if show_empty:
                empty_reports.append(f"{audio_dir.resolve().relative_to(Path.cwd()) if audio_dir.exists() else audio_dir}")
            continue

        lang_files = find_language_files(audio_dir, book_dir.resolve().name, languages, min_bytes)
        missing_langs_display: List[str] = []
        missing_lang_codes: List[str] = []
        for lang in languages:
            info = lang_files.get(lang)
            if info is None:
                missing_langs_display.append(lang)
                missing_lang_codes.append(lang)
            else:
                path, size = info
                if size < min_bytes:
                    readable_size = f"{size / 1024 / 1024:.2f} MB"
                    missing_langs_display.append(f"{lang} (<{min_bytes / 1024 / 1024:.2f} MB, {path.name}, {readable_size})")
                    missing_lang_codes.append(lang)
        if missing_langs_display:
            try:
                rel_path = audio_dir.resolve().relative_to(Path.cwd())
            except ValueError:
                rel_path = audio_dir
            missing_reports.append(f"{rel_path}: {', '.join(missing_langs_display)}")
            missing_map[audio_dir.resolve()] = sorted(set(missing_lang_codes))

    return missing_reports, empty_reports, missing_map

SUPPORTED_LANG_CODES = ["de", "en", "es", "fr", "hi", "ja", "ko", "pl", "pt"]


SUPPORTED_LANG_CODES = ["de", "en", "es", "fr", "hi", "ja", "ko", "pl", "pt"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that each audio directory contains all expected language files."
    )
    parser.add_argument(
        "--books",
        action="store_true",
        help="Only inspect the books/ directory.",
    )
    parser.add_argument(
        "--media",
        action="store_true",
        help="Only inspect the media/ directory.",
    )
    parser.add_argument(
        "--show-empty",
        action="store_true",
        help="Include directories with no audio files or missing audio/ subdirectory.",
    )
    parser.add_argument(
        "--min-size-mb",
        type=float,
        default=DEFAULT_MIN_SIZE_MB,
        help="Minimum file size (in MB) for an audio track to be considered valid (default: %(default)s).",
    )
    parser.add_argument(
        "--languages",
        type=str,
        default=",".join(SUPPORTED_LANG_CODES),
        help="Comma-separated list of required language codes "
        " (default: %(default)s). Example: --languages en,fr,de",
    )
    parser.add_argument(
        "--update-todo",
        action="store_true",
        help="For each directory with missing languages, ask whether to reset TODOIT statuses to pending.",
    )
    parser.add_argument(
        "--auto-confirm",
        action="store_true",
        help="When used with --update-todo, skip prompts and automatically reset statuses.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --update-todo, only show TODOIT commands that would be executed.",
    )
    return parser.parse_args()


def run_todoit_status(book_key: str, subitem: str, status: str, dry_run: bool) -> bool:
    cmd = [
        "todoit",
        "item",
        "status",
        "--list",
        TODO_LIST_KEY,
        "--item",
        book_key,
        "--subitem",
        subitem,
        "--status",
        status,
    ]
    if dry_run:
        print("    [dry-run]", " ".join(cmd))
        return True

    cmd = [
        "todoit",
        "item",
        "status",
        "--list",
        TODO_LIST_KEY,
        "--item",
        book_key,
        "--subitem",
        subitem,
        "--status",
        status,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        print(f"    ! Failed to update {book_key}:{subitem} -> {status} ({message})")
        return False
    print(f"    ✓ {book_key}:{subitem} -> {status}")
    return True


def process_todo_updates(missing_map: Dict[Path, List[str]], auto_confirm: bool, dry_run: bool) -> None:
    print("\n=== TODOIT status reset ===")
    for audio_dir, languages in sorted(missing_map.items()):
        if not languages:
            continue
        book_key = audio_dir.parent.name
        prompt = f"Reset TODO statuses for {book_key} ({', '.join(languages)})? [y/N]: "
        proceed = auto_confirm
        if not proceed:
            try:
                answer = input(prompt).strip().lower()
            except EOFError:
                print("  (no input received; skipping)")
                continue
            proceed = answer in {"y", "yes"}
        else:
            print(f"{prompt}auto-confirmed")

        if not proceed:
            continue

        for lang in languages:
            update_subitems = [
                f"audio_gen_{lang}",
                f"audio_dwn_{lang}",
            ]
            for subitem in update_subitems:
                run_todoit_status(book_key, subitem, "pending", dry_run=dry_run)


def main() -> None:
    args = parse_args()

    option_summary = (
        "Options:\n"
        "  --books        Only inspect the books/ directory (default: inspect both books/ and media/).\n"
        "  --media        Only inspect the media/ directory (default: inspect both books/ and media/).\n"
        "  --show-empty   Include directories with missing or empty audio/ folders in the report.\n"
        "  --min-size-mb  Minimum file size in MB for a valid audio file (default: 1.0).\n"
    )
    print(option_summary)

    inspect_books = args.books or not args.media
    inspect_media = args.media or not args.books

    min_bytes = int(args.min_size_mb * 1024 * 1024)
    languages = [lang.strip() for lang in args.languages.split(",") if lang.strip()]
    for lang in languages:
        if lang not in SUPPORTED_LANG_CODES:
            raise ValueError(f"Unsupported language code '{lang}'. Supported values: {SUPPORTED_LANG_CODES}")

    base_directories: List[Tuple[str, Path]] = []
    if inspect_books:
        base_directories.append(("books", Path("books")))
    if inspect_media:
        base_directories.append(("media", Path("media")))

    overall_missing: List[str] = []
    overall_empty: List[str] = []
    overall_missing_map: Dict[Path, List[str]] = {}

    for label, base_dir in base_directories:
        missing, empty, missing_map = inspect_base_directory(base_dir, languages, min_bytes, args.show_empty)

        if missing:
            overall_missing.append(f"\n[{label}]")
            overall_missing.extend(missing)
            overall_missing_map.update(missing_map)

        if args.show_empty and empty:
            overall_empty.append(f"\n[{label}]")
            overall_empty.extend(empty)

    if overall_missing:
        print("Missing or invalid audio tracks:")
        for line in overall_missing:
            print(line)
    else:
        print("All scanned audio directories contain the expected language files.")

    if args.show_empty and overall_empty:
        print("\nEmpty audio directories:")
        for line in overall_empty:
            print(line)

    if args.update_todo and overall_missing_map:
        process_todo_updates(overall_missing_map, args.auto_confirm, args.dry_run)


if __name__ == "__main__":
    main()

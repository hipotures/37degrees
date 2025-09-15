#!/usr/bin/env python3
"""
Generate a switching manifest for an interactive, multi-format dialogue experience.

For a given book folder (e.g., books/0012_harry_potter), this script:
- Picks primary format (A) from book.yaml's afa_analysis.formats
- Picks two alternates (B, C) using compatibility + evidence rules
- Builds segment structures for B, C (if missing) using existing utilities
- Emits a language-tagged JSON manifest that an audio player can use to
  offer 2 switch options at segment boundaries with short teasers.

Outputs:
  output/switch_manifests/<book_folder_name>_<lang>.json

Usage:
  python scripts/afa/generate_switch_manifest.py books/0012_harry_potter --langs pl,en
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / 'scripts' / 'lib'))
from afa_calculations import (
    calculate_depth_heat_composites,
    calculate_compatibility_score,
    generate_segment_structure,
    generate_detailed_prompts,
)


FORMATS = [
    "academic_analysis",
    "critical_debate",
    "temporal_context",
    "cultural_dimension",
    "social_perspective",
    "emotional_perspective",
    "exploratory_dialogue",
    "narrative_reconstruction",
]

DEFAULT_DURATIONS = {
    "exploratory_dialogue": 8,
    "narrative_reconstruction": 10,
    "emotional_perspective": 11,
    "temporal_context": 13,
    "social_perspective": 14,
    "critical_debate": 12,
    "cultural_dimension": 16,
    "academic_analysis": 15,
}


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def is_eligible(format_name: str, scores: Dict[str, Dict[str, Any]]) -> bool:
    """Heuristic minimum-evidence rules aligned with GPT guidelines.

    Uses score proxies; does not inspect research files here.
    """
    def s(key: str) -> float:
        v = scores.get(key, {}).get("value")
        return float(v) if v is not None else 0.0

    philosophical = s("philosophical_depth")
    structural = s("structural_complexity")
    innovation = s("innovation")
    controversy = s("controversy")
    cultural = s("cultural_phenomenon")
    contemporary = s("contemporary_reception")
    relevance = s("relevance")
    social = s("social_roles")

    if format_name == "academic_analysis" and structural < 4:
        return False
    if format_name == "critical_debate" and controversy < 6:
        return False

    if format_name == "academic_analysis":
        return (philosophical >= 6) or (structural >= 6) or (innovation >= 6)
    if format_name == "critical_debate":
        return (controversy >= 6) or (controversy >= 5 and (social >= 6 or relevance >= 6))
    if format_name == "temporal_context":
        return (relevance >= 6) or (cultural >= 6)
    if format_name == "cultural_dimension":
        return (cultural >= 6) or (contemporary >= 6)
    if format_name == "social_perspective":
        return (social >= 6) or (relevance >= 7)
    if format_name == "emotional_perspective":
        return (relevance >= 6)
    if format_name == "exploratory_dialogue":
        return True
    if format_name == "narrative_reconstruction":
        return (structural >= 6) or (structural >= 5 and cultural >= 6)
    return True


def pick_alternates(
    primary: str,
    ai_scores: Dict[str, Dict[str, Any]],
    switching_cfg: Dict[str, Any],
) -> Tuple[str, str, Dict[str, float]]:
    """Pick B and C based on compatibility and eligibility, guided by defaults.

    Returns: (B, C, compatibility_scores)
    """
    # Precedence: recommended alternatives from config
    recommended = switching_cfg.get("alternatives", {}).get(primary, [])
    candidates = [f for f in FORMATS if f != primary]

    scores: Dict[str, float] = {}
    for fmt in candidates:
        if not is_eligible(fmt, ai_scores):
            continue
        cs = calculate_compatibility_score(fmt, ai_scores)
        # Small bias if recommended by matrix
        if fmt in recommended:
            cs += 0.2
        scores[fmt] = cs

    # Fallback to any eligible if nothing scored
    if not scores:
        for fmt in candidates:
            if is_eligible(fmt, ai_scores):
                scores[fmt] = 0.0

    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
    if len(top) < 2:
        # Duplicate if only one found
        chosen = [top[0][0], recommended[0] if recommended else primary]
    else:
        chosen = [top[0][0], top[1][0]]

    return chosen[0], chosen[1], scores


def teaser_line(src_fmt: str, dst_fmt: str, title: str) -> str:
    templates = {
        ("critical_debate", "social_perspective"): "Switch to social lens: power, class, gender dynamics in action.",
        ("critical_debate", "cultural_dimension"): "Try the global journey: translations, adaptations, cross-cultural impact.",
        ("academic_analysis", "exploratory_dialogue"): "Prefer accessible discovery? Let's explore without heavy theory.",
        ("academic_analysis", "emotional_perspective"): "Shift to feelings-first: how '{t}' moves readers.",
        ("exploratory_dialogue", "narrative_reconstruction"): "Follow the case file: reconstruct key events and revelations.",
    }
    return templates.get((src_fmt, dst_fmt), f"Switch format to {dst_fmt} for a new angle on '{title}'.")


def build_format_payload(
    fmt_name: str,
    title: str,
    book_year: Any,
    themes: Dict[str, Any],
    depth: float,
    heat: float,
    existing: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build per-format payload with prompts and structure.

    If `existing` is provided (from book.yaml), reuse its structure and prompts.
    Otherwise, synthesize with generate_segment_structure + generate_detailed_prompts.
    """
    if existing:
        return {
            "name": fmt_name,
            "duration": existing.get("duration", DEFAULT_DURATIONS.get(fmt_name, 12)),
            "structure": existing.get("structure", []),
            "prompts": existing.get("prompts", {}),
        }

    duration = DEFAULT_DURATIONS.get(fmt_name, 12)
    fmt_dict = {"name": fmt_name, "duration": duration}
    structure = generate_segment_structure(fmt_dict, themes, depth, heat)
    prompts = generate_detailed_prompts(fmt_dict, title, themes, book_year)
    return {
        "name": fmt_name,
        "duration": duration,
        "structure": structure,
        "prompts": prompts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate switching manifest for a book")
    parser.add_argument("book_folder", help="Path to book folder (e.g., books/0012_harry_potter)")
    parser.add_argument("--langs", default="pl,en", help="Comma-separated languages to emit (default: pl,en)")
    args = parser.parse_args()

    book_dir = Path(args.book_folder)
    book_yaml = book_dir / "book.yaml"
    if not book_yaml.exists():
        print(f"ERROR: {book_yaml} not found")
        return 1

    data = load_yaml(book_yaml)
    book_info = data.get("book_info", {})
    title = book_info.get("title", book_dir.name)
    book_year = book_info.get("year", "")

    afa = data.get("afa_analysis", {})
    scores = afa.get("scores")
    formats = afa.get("formats", {})
    themes = afa.get("themes", {"universal": []})
    if not scores or not formats:
        print("ERROR: Missing afa_analysis.scores or formats in book.yaml")
        return 1

    # Primary format A from existing formats (first key)
    primary = list(formats.keys())[0]

    # Prepare ai_response-like structure
    ai_response = {
        "raw_scores": {k: {"value": v} for k, v in scores.items() if k not in ("total", "percentile")}
    }
    depth, depth_cat, heat, heat_cat = calculate_depth_heat_composites(ai_response)

    # Load switching matrix
    switch_cfg_path = Path("config/afa_switching_matrix.yaml")
    switch_cfg = yaml.safe_load(switch_cfg_path.read_text(encoding="utf-8")) if switch_cfg_path.exists() else {"alternatives": {}}

    # Pick B and C
    alt_b, alt_c, comp_scores = pick_alternates(primary, ai_response["raw_scores"], switch_cfg)

    # Build payloads for A, B, C
    a_payload = build_format_payload(primary, title, book_year, themes, depth, heat, existing=formats.get(primary))
    b_payload = build_format_payload(alt_b, title, book_year, themes, depth, heat)
    c_payload = build_format_payload(alt_c, title, book_year, themes, depth, heat)

    # Switch offers at end of segment 1 and 3 in A (if enough segments)
    a_segments = a_payload.get("structure", [])
    offer_points = []
    if len(a_segments) >= 1:
        offer_points.append(a_segments[0].get("time_range", "03:00-06:00").split("-")[-1])
    if len(a_segments) >= 3:
        offer_points.append(a_segments[2].get("time_range", "09:00-12:00").split("-")[-1])

    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    out_dir = Path("output/switch_manifests")
    out_dir.mkdir(parents=True, exist_ok=True)

    for lang in langs:
        manifest = {
            "book": {
                "id": book_dir.name,
                "title": title,
                "language": lang,
            },
            "mode": "tts",  # on-demand TTS recommended
            "root": {
                "on_ramp_text": f"Welcome to '{title}'. Choose your vibe: stay in {primary} or jump to {alt_b}.",
                "initial_options": [primary, alt_b],
            },
            "formats": {
                primary: a_payload,
                alt_b: b_payload,
                alt_c: c_payload,
            },
            "switch_offers": [
                {
                    "at": offer_points[0] if len(offer_points) > 0 else "03:00",
                    "from": primary,
                    "options": [
                        {"to": alt_b, "teaser": teaser_line(primary, alt_b, title)},
                        {"to": alt_c, "teaser": teaser_line(primary, alt_c, title)},
                    ],
                },
            ] + (
                [
                    {
                        "at": offer_points[1],
                        "from": primary,
                        "options": [
                            {"to": alt_b, "teaser": teaser_line(primary, alt_b, title)},
                            {"to": alt_c, "teaser": teaser_line(primary, alt_c, title)},
                        ],
                    }
                ]
                if len(offer_points) > 1
                else []
            ),
            "notes": {
                "compatibility_scores": comp_scores,
                "depth": depth,
                "heat": heat,
                "evidence_guardrails": "eligibility enforced via score thresholds",
            },
        }

        out_path = out_dir / f"{book_dir.name}_{lang}.json"
        out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


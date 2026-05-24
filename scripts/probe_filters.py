"""CLI probe: filter catalog by preferences and print candidate summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.store import load_catalog
from app.integration.filters import apply_filters, empty_result_suggestions
from app.logging_config import setup_logging
from app.models import BudgetTier, UserPreferences


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe deterministic restaurant filters.")
    parser.add_argument("--location", "-l", required=True, help="City, e.g. Bangalore")
    parser.add_argument("--budget", "-b", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", "-c", default="", help="Cuisine filter (optional)")
    parser.add_argument("--min-rating", "-r", type=float, default=0.0, help="Minimum rating")
    parser.add_argument("--extras", default="", help="Additional prefs (not filtered in Phase 2)")
    parser.add_argument("--sample", "-n", type=int, default=5, help="Rows to print")
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()
    prefs = UserPreferences(
        location=args.location,
        budget=args.budget,  # type: ignore[arg-type]
        cuisine=args.cuisine,
        minRating=args.min_rating,
        additionalPreferences=args.extras,
    )

    catalog = load_catalog()
    result = apply_filters(catalog, prefs)

    print(f"Catalog size: {len(catalog)}")
    print(f"Filters applied: {', '.join(result.applied_filters)}")
    print(f"Before filter: {result.total_before_filter}")
    print(f"After filter:  {result.total_after_filter}")
    print(f"Candidates returned (capped): {len(result.candidates)}")

    if not result.candidates:
        print("\nNo matches. Suggestions:")
        for tip in empty_result_suggestions(prefs):
            print(f"  - {tip}")
        return

    print(f"\n--- Top {min(args.sample, len(result.candidates))} candidates ---")
    for r in result.candidates[: args.sample]:
        area = f"{r.area}, " if r.area else ""
        cuisines = ", ".join(r.cuisine[:3])
        print(
            f"  [{r.id}] {r.name} | {area}{r.location} | "
            f"{cuisines} | rating={r.rating} | {r.budget_tier}"
        )


if __name__ == "__main__":
    main()

"""Manual smoke test: filter catalog then call LLM (requires LLM_API_KEY)."""

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
from app.integration.filters import apply_filters
from app.llm.engine import rank_and_explain
from app.logging_config import setup_logging
from app.models import UserPreferences


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Smoke test LLM ranking.")
    parser.add_argument("-l", "--location", default="Bangalore")
    parser.add_argument("-b", "--budget", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("-c", "--cuisine", default="Italian")
    parser.add_argument("-r", "--min-rating", type=float, default=4.0)
    parser.add_argument("--limit", type=int, default=8, help="Max candidates sent to LLM")
    args = parser.parse_args()

    prefs = UserPreferences(
        location=args.location,
        budget=args.budget,  # type: ignore[arg-type]
        cuisine=args.cuisine,
        minRating=args.min_rating,
        additionalPreferences="family-friendly",
    )

    catalog = load_catalog()
    filtered = apply_filters(catalog, prefs)
    candidates = filtered.candidates[: args.limit]
    print(f"Sending {len(candidates)} candidates to LLM (from {filtered.total_after_filter} matches)")

    if not candidates:
        print("No candidates to rank.")
        return

    result = rank_and_explain(candidates, prefs)
    print(f"\nFallback used: {result.used_fallback}")
    if result.parse_error:
        print(f"Parse error: {result.parse_error}")
    if result.summary:
        print(f"\nSummary: {result.summary}")

    print("\nRecommendations:")
    for item in result.recommendations:
        restaurant = next(c for c in candidates if c.id == item.restaurant_id)
        print(f"  #{item.rank} {restaurant.name} ({restaurant.rating})")
        print(f"     {item.explanation}")


if __name__ == "__main__":
    main()

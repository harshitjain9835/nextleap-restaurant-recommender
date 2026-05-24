"""Print sample normalized restaurants after loading the catalog."""

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

from app.logging_config import setup_logging
from app.data.store import get_distinct_cuisines, get_distinct_locations, load_catalog


def main() -> None:
    setup_logging()
    catalog = load_catalog()
    print(f"Loaded {len(catalog)} restaurants\n")
    print("Cities:", ", ".join(get_distinct_locations()[:15]), "...")
    print("Cuisines (sample):", ", ".join(get_distinct_cuisines()[:10]), "...\n")
    print("--- Sample (5) ---")
    for r in catalog[:5]:
        area = f"{r.area}, " if r.area else ""
        cuisines = ", ".join(r.cuisine[:3]) or "N/A"
        print(
            f"  [{r.id}] {r.name} | {area}{r.location} | "
            f"{cuisines} | rating={r.rating} | {r.estimated_cost} | {r.budget_tier}"
        )


if __name__ == "__main__":
    main()

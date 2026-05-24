from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models import Restaurant, UserPreferences
from app.llm.engine import rank_and_explain

prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")
candidates = [
    Restaurant(
        id="r1",
        name="Alpha Bistro",
        location="Bangalore",
        cuisine=["Italian"],
        rating=4.6,
        estimatedCost="₹800 for two",
        budgetTier="high",
    )
]

result = rank_and_explain(candidates, prefs)
print(f"used_fallback={result.used_fallback}")
print(f"summary={result.summary!r}")
for item in result.recommendations:
    print(f"rank={item.rank} id={item.restaurant_id}")
    print(f"explanation={item.explanation}")
    print()

from __future__ import annotations

from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    print("Importing modules...", flush=True)
    from app.models import Restaurant, UserPreferences
    from app.llm.engine import rank_and_explain
    from app.config import get_settings

    print("Creating test data...", flush=True)
    settings = get_settings()
    print(f"  LLM_MODEL={settings.llm_model}", flush=True)
    print(f"  LLM_BASE_URL={settings.llm_base_url}", flush=True)
    print(f"  Has LLM_API_KEY: {bool(settings.llm_api_key)}", flush=True)

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

    print("\nCalling LLM engine...", flush=True)
    result = rank_and_explain(candidates, prefs)
    
    print(f"\n✓ LLM call completed!")
    print(f"  used_fallback={result.used_fallback}")
    print(f"  parse_error={result.parse_error}")
    print(f"  summary={result.summary!r}")
    print(f"\nRecommendations:")
    for item in result.recommendations:
        print(f"  rank={item.rank} id={item.restaurant_id}")
        print(f"  explanation={item.explanation[:100]}...")
        
except Exception as e:
    print(f"\n✗ Error: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

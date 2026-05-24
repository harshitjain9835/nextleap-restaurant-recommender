#!/usr/bin/env python3
import os
import sys

os.chdir(r'g:\nextleap\projects')
sys.path.insert(0, r'g:\nextleap\projects')

try:
    from app.config import Settings
    from app.models import Restaurant, UserPreferences
    from app.llm.engine import rank_and_explain

    settings = Settings()
    print("✓ Config loaded:")
    print(f"  LLM_MODEL={settings.llm_model}")
    print(f"  LLM_BASE_URL={settings.llm_base_url}")
    print(f"  LLM_API_KEY={'<SET>' if settings.llm_api_key else 'NOT SET'}")

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

    print("\nCalling groq LLM...")
    result = rank_and_explain(candidates, prefs, settings=settings)

    print(f"✓ LLM call completed!")
    print(f"  Used fallback: {result.used_fallback}")
    if result.parse_error:
        print(f"  Parse error: {result.parse_error}")
    if result.summary:
        print(f"  Summary: {result.summary}")
    if result.recommendations:
        print(f"  Got {len(result.recommendations)} recommendation(s)")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

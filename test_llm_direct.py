#!/usr/bin/env python3
import os
import sys

os.chdir(r'g:\nextleap\projects')
sys.path.insert(0, r'g:\nextleap\projects')

print("Current directory:", os.getcwd())
print("Testing LLM call with direct Settings instantiation...\n")

# Direct instantiation without cache
from app.config import Settings

settings = Settings(_env_file='.env')
print(f"✓ Settings loaded directly:")
print(f"  LLM_MODEL={settings.llm_model}")
print(f"  LLM_BASE_URL={settings.llm_base_url}")
print(f"  LLM_API_KEY={'<SET>' if settings.llm_api_key else 'NOT SET'}")

if not settings.llm_base_url:
    print("\n⚠️  LLM_BASE_URL is still None! Check .env file.")
    sys.exit(1)

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

print("\nCalling LLM with groq...")
result = rank_and_explain(candidates, prefs, settings=settings)

print(f"✓ LLM call completed!")
print(f"  Used fallback: {result.used_fallback}")
if result.parse_error:
    print(f"  Parse error: {result.parse_error}")
if result.summary:
    print(f"  Summary: {result.summary}")

print(f"\nRecommendations:")
for item in result.recommendations:
    print(f"  Rank {item.rank}: {item.restaurant_id}")
    print(f"    {item.explanation[:80]}...")

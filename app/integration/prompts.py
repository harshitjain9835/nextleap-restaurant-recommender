"""Prompt assembly for LLM ranking and explanations."""

from __future__ import annotations

import json

from app.models import Restaurant, UserPreferences

SYSTEM_PROMPT = """You are a restaurant recommendation assistant for a Zomato-style app.

Rules:
- You may ONLY recommend restaurants from the CANDIDATES list below.
- Every restaurantId in your response MUST appear in CANDIDATES.
- Do NOT invent restaurants, ratings, or prices.
- Return valid JSON only, matching the schema exactly.
- Consider additionalPreferences as soft signals when ranking."""

RESPONSE_SCHEMA = {
    "summary": "Optional 1-2 sentence overview of the shortlist",
    "recommendations": [
        {
            "restaurantId": "id from CANDIDATES",
            "rank": 1,
            "explanation": "1-3 sentences why this fits the user",
        }
    ],
}

FIX_JSON_PROMPT = (
    "Your previous response was not valid JSON matching the schema. "
    "Return ONLY corrected JSON with no markdown or extra text."
)


def compact_candidate(restaurant: Restaurant) -> dict:
    return {
        "restaurantId": restaurant.id,
        "name": restaurant.name,
        "location": restaurant.location,
        "area": restaurant.area or None,
        "cuisine": restaurant.cuisine,
        "rating": restaurant.rating,
        "estimatedCost": restaurant.estimated_cost,
        "budgetTier": restaurant.budget_tier,
    }


def build_user_prompt(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    top_k: int,
) -> str:
    prefs_payload = preferences.model_dump(by_alias=True)
    candidate_payload = [compact_candidate(c) for c in candidates]
    schema_json = json.dumps(RESPONSE_SCHEMA, indent=2)

    return f"""User preferences:
{json.dumps(prefs_payload, indent=2)}

CANDIDATES ({len(candidate_payload)} restaurants):
{json.dumps(candidate_payload, indent=2)}

Tasks:
1. Rank the top {top_k} restaurants for these preferences.
2. For each, write a concise explanation (1-3 sentences) referencing specific attributes.
3. Include a brief summary of the overall shortlist.

Return JSON matching this schema:
{schema_json}

Use only restaurantId values from CANDIDATES. ranks must be 1..{top_k} with no duplicates."""


def build_messages(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    top_k: int,
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(preferences, candidates, top_k)},
    ]


def build_fix_messages(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    top_k: int,
    invalid_response: str,
) -> list[dict[str, str]]:
    messages = build_messages(preferences, candidates, top_k)
    messages.append({"role": "assistant", "content": invalid_response[:4000]})
    messages.append({"role": "user", "content": FIX_JSON_PROMPT})
    return messages

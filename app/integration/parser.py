"""Parse and validate LLM JSON responses."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.models import LLMRecommendationItem, LLMRankingResult, Restaurant, UserPreferences

logger = logging.getLogger(__name__)

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)
_MAX_EXPLANATION_LEN = 500


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from raw LLM text (handles markdown fences)."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty LLM response")

    fence = _JSON_FENCE.search(raw)
    if fence:
        raw = fence.group(1).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(raw[start : end + 1])


def _truncate_explanation(text: str) -> str:
    text = (text or "").strip()
    if len(text) <= _MAX_EXPLANATION_LEN:
        return text
    cut = text[:_MAX_EXPLANATION_LEN].rsplit(" ", 1)[0]
    return cut + "…"


def template_explanation(restaurant: Restaurant, preferences: UserPreferences) -> str:
    """Fallback explanation when LLM output is unavailable."""
    cuisine = preferences.cuisine.strip() or "your preferred"
    extras = preferences.additional_preferences.strip()
    base = (
        f"{restaurant.name} is a strong match in {preferences.location} with "
        f"{', '.join(restaurant.cuisine[:2]) or cuisine} cuisine, "
        f"rating {restaurant.rating}, and {restaurant.budget_tier} budget tier."
    )
    if extras:
        base += f" It may also suit your preference for: {extras}."
    return base


def build_fallback_rankings(
    candidates: list[Restaurant],
    preferences: UserPreferences,
    top_k: int,
) -> LLMRankingResult:
    """Top K by rating with template explanations (filter order = rating desc)."""
    sorted_candidates = sorted(
        candidates,
        key=lambda r: (-r.rating, r.name.lower(), r.id),
    )[:top_k]
    items = [
        LLMRecommendationItem(
            restaurantId=r.id,
            rank=i + 1,
            explanation=template_explanation(r, preferences),
        )
        for i, r in enumerate(sorted_candidates)
    ]
    summary = (
        f"Top {len(items)} rated matches in {preferences.location} "
        f"for {preferences.budget} budget."
        if items
        else None
    )
    return LLMRankingResult(
        summary=summary,
        recommendations=items,
        usedFallback=True,
    )


def _validate_items(
    raw_items: list[Any],
    valid_ids: set[str],
    top_k: int,
) -> list[LLMRecommendationItem]:
    seen_ids: set[str] = set()
    seen_ranks: set[int] = set()
    valid: list[LLMRecommendationItem] = []

    for entry in raw_items:
        if not isinstance(entry, dict):
            continue
        rid = str(entry.get("restaurantId", "")).strip()
        if not rid or rid not in valid_ids or rid in seen_ids:
            if rid and rid not in valid_ids:
                logger.warning("Dropping unknown restaurantId from LLM: %s", rid)
            continue
        try:
            rank = int(entry.get("rank", 0))
        except (TypeError, ValueError):
            continue
        if rank < 1 or rank in seen_ranks:
            continue
        explanation = _truncate_explanation(str(entry.get("explanation", "")))
        if not explanation:
            explanation = "Recommended based on your preferences."
        valid.append(
            LLMRecommendationItem(
                restaurantId=rid,
                rank=rank,
                explanation=explanation,
            )
        )
        seen_ids.add(rid)
        seen_ranks.add(rank)
        if len(valid) >= top_k:
            break

    valid.sort(key=lambda x: x.rank)
    return valid


def backfill_items(
    items: list[LLMRecommendationItem],
    candidates: list[Restaurant],
    preferences: UserPreferences,
    top_k: int,
) -> list[LLMRecommendationItem]:
    """Fill remaining slots from filter order without duplicating IDs."""
    used = {i.restaurant_id for i in items}
    sorted_candidates = sorted(
        candidates,
        key=lambda r: (-r.rating, r.name.lower(), r.id),
    )
    result = list(items)
    next_rank = max((i.rank for i in result), default=0) + 1
    for r in sorted_candidates:
        if len(result) >= top_k:
            break
        if r.id in used:
            continue
        result.append(
            LLMRecommendationItem(
                restaurantId=r.id,
                rank=next_rank,
                explanation=template_explanation(r, preferences),
            )
        )
        used.add(r.id)
        next_rank += 1
    result.sort(key=lambda x: x.rank)
    for idx, item in enumerate(result[:top_k], start=1):
        item.rank = idx
    return result[:top_k]


def parse_llm_response(
    text: str,
    candidates: list[Restaurant],
    preferences: UserPreferences,
    top_k: int,
) -> LLMRankingResult:
    """
    Parse LLM JSON into LLMRankingResult.
    Drops unknown IDs, deduplicates, backfills to top_k if needed.
    """
    payload = extract_json_object(text)
    valid_ids = {c.id for c in candidates}
    raw_items = payload.get("recommendations") or []
    if not isinstance(raw_items, list):
        raw_items = []

    items = _validate_items(raw_items, valid_ids, top_k)
    if not items and candidates:
        raise ValueError("No valid recommendations in LLM response")

    items = backfill_items(items, candidates, preferences, top_k)
    summary = payload.get("summary")
    if summary is not None:
        summary = str(summary).strip() or None

    return LLMRankingResult(summary=summary, recommendations=items, usedFallback=False)

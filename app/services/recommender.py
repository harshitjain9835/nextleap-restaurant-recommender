"""Orchestrator service for end-to-end restaurant recommendations."""

from __future__ import annotations

from typing import cast

from app.config import Settings, get_settings
from app.data.store import load_catalog
from app.integration.filters import apply_filters, empty_result_suggestions
from app.llm.engine import rank_and_explain
from app.models import (
    CandidateList,
    LLMRankingResult,
    Recommendation,
    RecommendationMeta,
    RecommendationResponse,
    Restaurant,
    UserPreferences,
)

_MAX_ADDITIONAL_PREFERENCES_LENGTH = 200
_VALID_BUDGETS = frozenset({"low", "medium", "high"})


def _sanitize_preferences(preferences: UserPreferences) -> UserPreferences:
    preferences = preferences.model_copy(deep=True)
    if preferences.min_rating < 0:
        preferences.min_rating = 0.0
    elif preferences.min_rating > 5.0:
        preferences.min_rating = 5.0

    extras = (preferences.additional_preferences or "").strip()
    if len(extras) > _MAX_ADDITIONAL_PREFERENCES_LENGTH:
        extras = extras[:_MAX_ADDITIONAL_PREFERENCES_LENGTH].rsplit(" ", 1)[0]
    preferences.additional_preferences = extras
    return preferences


def _validate_preferences(preferences: UserPreferences) -> None:
    if not preferences.location.strip():
        raise ValueError("location is required")
    if preferences.budget not in _VALID_BUDGETS:
        raise ValueError("budget must be one of: low, medium, high")


def _merge_recommendations(
    items: list[Recommendation],
    candidates: list[Restaurant],
) -> list[Recommendation]:
    by_id = {restaurant.id: restaurant for restaurant in candidates}
    merged: list[Recommendation] = []
    for item in items:
        restaurant = by_id.get(item.restaurant_id)
        if restaurant is None:
            continue
        merged.append(
            Recommendation(
                restaurantId=item.restaurant_id,
                name=restaurant.name,
                cuisine=restaurant.cuisine,
                rating=restaurant.rating,
                estimatedCost=restaurant.estimated_cost,
                rank=item.rank,
                explanation=item.explanation,
            )
        )
    return merged


def recommend(
    preferences: UserPreferences,
    *,
    settings: Settings | None = None,
) -> RecommendationResponse:
    """Run the full recommendation flow from catalog to response."""
    settings = settings or get_settings()
    preferences = _sanitize_preferences(preferences)
    _validate_preferences(preferences)

    catalog = load_catalog()
    candidate_list = apply_filters(catalog, preferences, settings=settings)

    if not candidate_list.candidates:
        return RecommendationResponse(
            summary=None,
            recommendations=[],
            suggestions=empty_result_suggestions(preferences),
            meta=RecommendationMeta(
                candidatesConsidered=len(candidate_list.candidates),
                filtersApplied=candidate_list.applied_filters,
                usedFallback=False,
            ),
        )

    llm_result = rank_and_explain(candidate_list.candidates, preferences, settings=settings)
    recommendations = _merge_recommendations(llm_result.recommendations, candidate_list.candidates)

    return RecommendationResponse(
        summary=llm_result.summary,
        recommendations=recommendations,
        suggestions=[],
        meta=RecommendationMeta(
            candidatesConsidered=len(candidate_list.candidates),
            filtersApplied=candidate_list.applied_filters,
            usedFallback=llm_result.used_fallback,
        ),
    )

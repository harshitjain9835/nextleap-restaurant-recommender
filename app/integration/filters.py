"""Deterministic filter engine: catalog + preferences -> CandidateList."""

from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.data.normalize import canonicalize_city
from app.models import CandidateList, Restaurant, UserPreferences

logger = logging.getLogger(__name__)

EMPTY_RESULT_SUGGESTIONS = [
    "Try a nearby city or check the spelling of your location.",
    "Lower your minimum rating.",
    "Choose a different cuisine or leave cuisine blank.",
    "Try a different budget tier (low, medium, or high).",
]


def normalize_location(location: str) -> str:
    """Canonicalize user location for equality matching."""
    text = (location or "").strip()
    if not text:
        return ""
    canonical = canonicalize_city(text)
    return canonical or text.title()


def matches_location(restaurant: Restaurant, user_location: str) -> bool:
    """Case-insensitive equality on canonical city (architecture §3.5.1)."""
    target = normalize_location(user_location)
    if not target:
        return False
    return restaurant.location.strip().lower() == target.lower()


def matches_cuisine(restaurant: Restaurant, user_cuisine: str) -> bool:
    """
    Case-insensitive match: user cuisine equals or is contained in a restaurant tag.
    Skipped when user_cuisine is blank (caller responsibility).
    """
    query = (user_cuisine or "").strip().lower()
    if not query:
        return True
    for tag in restaurant.cuisine:
        tag_lower = tag.strip().lower()
        if tag_lower == query or query in tag_lower or tag_lower in query:
            return True
    return False


def matches_min_rating(restaurant: Restaurant, min_rating: float) -> bool:
    return restaurant.rating >= min_rating


def matches_budget(restaurant: Restaurant, budget: str) -> bool:
    return restaurant.budget_tier == budget


def _sort_key(restaurant: Restaurant) -> tuple:
    """Rating desc, then name asc for stable ordering."""
    return (-restaurant.rating, restaurant.name.lower(), restaurant.id)


def apply_cap(candidates: list[Restaurant], max_candidates: int) -> list[Restaurant]:
    sorted_candidates = sorted(candidates, key=_sort_key)
    return sorted_candidates[:max_candidates]


def empty_result_suggestions(preferences: UserPreferences) -> list[str]:
    """User guidance when no restaurants match filters (edge-cases FILT-12)."""
    tips = list(EMPTY_RESULT_SUGGESTIONS)
    if preferences.min_rating > 4.0:
        tips.insert(0, f"Your minimum rating ({preferences.min_rating}) is very high.")
    if preferences.cuisine.strip():
        tips.insert(
            0,
            f"No matches for '{preferences.cuisine}' — try a broader cuisine label.",
        )
    return tips


def apply_filters(
    catalog: list[Restaurant],
    preferences: UserPreferences,
    settings: Settings | None = None,
) -> CandidateList:
    """
    Filter pipeline (in order):
    location -> cuisine -> min rating -> budget -> cap (MAX_CANDIDATES).

    Additional preferences are deferred to the LLM (Phase 3).
    """
    settings = settings or get_settings()
    total_before = len(catalog)
    applied: list[str] = []
    current = list(catalog)

    # Location
    applied.append("location")
    user_city = normalize_location(preferences.location)
    current = [r for r in current if matches_location(r, user_city)]
    logger.debug("After location (%s): %d", user_city, len(current))

    # Cuisine (optional)
    cuisine_query = (preferences.cuisine or "").strip()
    if cuisine_query:
        applied.append("cuisine")
        current = [r for r in current if matches_cuisine(r, cuisine_query)]
        logger.debug("After cuisine (%s): %d", cuisine_query, len(current))

    # Minimum rating
    if preferences.min_rating > 0:
        applied.append("minRating")
        current = [r for r in current if matches_min_rating(r, preferences.min_rating)]
        logger.debug("After minRating (>=%s): %d", preferences.min_rating, len(current))

    # Budget
    applied.append("budget")
    current = [r for r in current if matches_budget(r, preferences.budget)]
    logger.debug("After budget (%s): %d", preferences.budget, len(current))

    total_after_filters = len(current)

    # Cap for LLM token control (sort by rating desc either way)
    if len(current) > settings.max_candidates:
        applied.append("cap")
    current = apply_cap(current, settings.max_candidates)

    return CandidateList(
        candidates=current,
        appliedFilters=applied,
        totalBeforeFilter=total_before,
        totalAfterFilter=total_after_filters,
    )

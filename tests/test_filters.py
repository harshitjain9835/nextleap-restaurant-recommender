"""Unit tests for filter engine (Phase 2)."""

import pytest

from app.config import Settings
from app.integration.filters import (
    apply_cap,
    apply_filters,
    empty_result_suggestions,
    matches_cuisine,
    matches_location,
    normalize_location,
)
from app.models import Restaurant, UserPreferences


@pytest.fixture
def filter_settings() -> Settings:
    # model_construct avoids .env overriding MAX_CANDIDATES during tests.
    return Settings.model_construct(
        max_candidates=3,
        budget_low_max=300,
        budget_medium_max=600,
        use_parquet_cache=False,
        hf_dataset_id="test",
    )


@pytest.fixture
def catalog() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Italian Place",
            location="Bangalore",
            area="Koramangala",
            cuisine=["Italian", "Pizza"],
            rating=4.5,
            estimatedCost="₹800 for two",
            budgetTier="high",
        ),
        Restaurant(
            id="r2",
            name="Budget Dosa",
            location="Bangalore",
            area="BTM",
            cuisine=["South Indian"],
            rating=3.8,
            estimatedCost="₹200 for two",
            budgetTier="low",
        ),
        Restaurant(
            id="r3",
            name="Mid Cafe",
            location="Bangalore",
            cuisine=["Cafe", "Chinese"],
            rating=4.0,
            estimatedCost="₹500 for two",
            budgetTier="medium",
        ),
        Restaurant(
            id="r4",
            name="Delhi Kebab",
            location="Delhi",
            cuisine=["North Indian"],
            rating=4.2,
            estimatedCost="₹600 for two",
            budgetTier="medium",
        ),
        Restaurant(
            id="r5",
            name="Low Rated Italian",
            location="Bangalore",
            cuisine=["Italian"],
            rating=3.0,
            estimatedCost="₹700 for two",
            budgetTier="medium",
        ),
    ]


def test_normalize_location_aliases():
    assert normalize_location("bengaluru") == "Bangalore"
    assert normalize_location("Bangalore") == "Bangalore"


def test_matches_location_case_insensitive(catalog: list[Restaurant]):
    assert matches_location(catalog[0], "bangalore")
    assert not matches_location(catalog[0], "Delhi")


def test_matches_cuisine_exact_and_partial(catalog: list[Restaurant]):
    assert matches_cuisine(catalog[0], "Italian")
    assert matches_cuisine(catalog[0], "italian")
    assert matches_cuisine(catalog[2], "Chinese")
    assert not matches_cuisine(catalog[0], "Mexican")


def test_apply_filters_location_only(catalog: list[Restaurant], filter_settings: Settings):
    prefs = UserPreferences(location="Bangalore", budget="low")
    # budget=low should narrow to r2 only among bangalore... wait budget low only r2
    prefs_all_budget = UserPreferences(location="Bangalore", budget="medium")
    # get all bangalore with medium: r3, r5
    result = apply_filters(
        catalog,
        UserPreferences(location="Bangalore", budget="low"),
        settings=filter_settings,
    )
    assert result.total_before_filter == 5
    assert len(result.candidates) == 1
    assert result.candidates[0].id == "r2"
    assert "location" in result.applied_filters
    assert "budget" in result.applied_filters


def test_apply_filters_area_within_bangalore(catalog: list[Restaurant], filter_settings: Settings):
    prefs = UserPreferences(location="Bangalore", area="Koramangala", budget="high")
    result = apply_filters(catalog, prefs, settings=filter_settings)
    assert len(result.candidates) == 1
    assert result.candidates[0].id == "r1"
    assert "area" in result.applied_filters


def test_apply_filters_cuisine_and_rating(catalog: list[Restaurant], filter_settings: Settings):
    # r1: Italian, 4.5, high — no match for medium budget
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        minRating=4.0,
    )
    result = apply_filters(catalog, prefs, settings=filter_settings)
    assert result.candidates == []

    prefs_match = UserPreferences(
        location="Bangalore",
        budget="high",
        cuisine="Italian",
        minRating=4.0,
    )
    result2 = apply_filters(catalog, prefs_match, settings=filter_settings)
    assert {r.id for r in result2.candidates} == {"r1"}


def test_apply_filters_empty_for_delhi_italian(catalog: list[Restaurant], filter_settings: Settings):
    prefs = UserPreferences(location="Delhi", budget="medium", cuisine="Italian")
    result = apply_filters(catalog, prefs, settings=filter_settings)
    assert result.candidates == []
    assert result.total_after_filter == 0
    assert len(empty_result_suggestions(prefs)) >= 1


def test_apply_filters_cap(filter_settings: Settings):
    many_high = [
        Restaurant(
            id=f"r_cap_{i}",
            name=f"High Place {i}",
            location="Bangalore",
            cuisine=["North Indian"],
            rating=3.5 + i * 0.1,
            estimatedCost="₹800 for two",
            budgetTier="high",
        )
        for i in range(10)
    ]
    prefs = UserPreferences(location="Bangalore", budget="high")
    result = apply_filters(many_high, prefs, settings=filter_settings)
    assert result.total_after_filter == 10
    assert len(result.candidates) == filter_settings.max_candidates
    assert "cap" in result.applied_filters
    ratings = [r.rating for r in result.candidates]
    assert ratings == sorted(ratings, reverse=True)


def test_apply_cap_stable_sort(filter_settings: Settings, catalog: list[Restaurant]):
    capped = apply_cap(catalog, 2)
    assert len(capped) == 2
    assert capped[0].rating >= capped[1].rating


def test_apply_filters_skips_cuisine_when_blank(catalog: list[Restaurant], filter_settings: Settings):
    prefs = UserPreferences(location="Delhi", budget="medium", cuisine="")
    result = apply_filters(catalog, prefs, settings=filter_settings)
    assert "cuisine" not in result.applied_filters
    assert len(result.candidates) == 1
    assert result.candidates[0].id == "r4"


def test_apply_filters_skips_min_rating_when_zero(catalog: list[Restaurant], filter_settings: Settings):
    prefs = UserPreferences(location="Bangalore", budget="low", minRating=0.0)
    result = apply_filters(catalog, prefs, settings=filter_settings)
    assert "minRating" not in result.applied_filters

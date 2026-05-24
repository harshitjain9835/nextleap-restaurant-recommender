"""Validate domain models (Phase 0)."""

from app.models import CandidateList, Restaurant, UserPreferences


def test_restaurant_roundtrip_aliases():
    r = Restaurant(
        id="r_1",
        name="Cafe",
        location="Bangalore",
        cuisine=["Italian"],
        rating=4.0,
        estimatedCost="₹400 for two",
        budgetTier="medium",
    )
    data = r.model_dump(by_alias=True)
    assert data["estimatedCost"] == "₹400 for two"
    assert data["budgetTier"] == "medium"


def test_user_preferences_defaults():
    p = UserPreferences(location="Bangalore", budget="low")
    assert p.min_rating == 0.0
    assert p.cuisine == ""


def test_candidate_list():
    c = CandidateList(
        candidates=[],
        appliedFilters=["location"],
        totalBeforeFilter=100,
        totalAfterFilter=0,
    )
    assert c.total_after_filter == 0

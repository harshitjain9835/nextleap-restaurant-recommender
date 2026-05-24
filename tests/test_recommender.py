"""Tests for recommendation orchestration service (Phase 4)."""

from app.models import (
    CandidateList,
    LLMRankingResult,
    LLMRecommendationItem,
    Recommendation,
    RecommendationMeta,
    RecommendationResponse,
    Restaurant,
    UserPreferences,
)
from app.services.recommender import recommend


def _catalog() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Alpha Bistro",
            location="Bangalore",
            cuisine=["Italian"],
            rating=4.6,
            estimatedCost="₹800",
            budgetTier="high",
        ),
        Restaurant(
            id="r2",
            name="Beta Cafe",
            location="Bangalore",
            cuisine=["Italian", "Pizza"],
            rating=4.2,
            estimatedCost="₹500",
            budgetTier="medium",
        ),
    ]


def test_recommend_merges_llm_ranking(monkeypatch):
    prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")
    catalog = _catalog()

    candidate_list = CandidateList(
        candidates=[catalog[0], catalog[1]],
        appliedFilters=["location", "cuisine", "budget"],
        totalBeforeFilter=2,
        totalAfterFilter=2,
    )

    monkeypatch.setattr("app.services.recommender.load_catalog", lambda: catalog)
    monkeypatch.setattr("app.services.recommender.apply_filters", lambda catalog, preferences, settings=None: candidate_list)
    monkeypatch.setattr(
        "app.services.recommender.rank_and_explain",
        lambda candidates, preferences, settings=None: LLMRankingResult(
            summary="Best choices for Bangalore",
            recommendations=[
                LLMRecommendationItem(
                    restaurantId="r2",
                    rank=1,
                    explanation="Great value and good Italian options.",
                ),
                LLMRecommendationItem(
                    restaurantId="r1",
                    rank=2,
                    explanation="High rating and premium experience.",
                ),
            ],
            usedFallback=False,
        ),
    )

    response = recommend(prefs)

    assert response.summary == "Best choices for Bangalore"
    assert response.meta is not None
    assert response.meta.candidates_considered == 2
    assert response.meta.filters_applied == ["location", "cuisine", "budget"]
    assert response.meta.used_fallback is False
    assert len(response.recommendations) == 2
    assert response.recommendations[0].restaurant_id == "r2"
    assert response.recommendations[0].name == "Beta Cafe"
    assert response.recommendations[1].restaurant_id == "r1"


def test_recommend_returns_suggestions_when_no_candidates(monkeypatch):
    prefs = UserPreferences(location="Bangalore", budget="medium")
    catalog = _catalog()

    empty_list = CandidateList(
        candidates=[],
        appliedFilters=["location", "budget"],
        totalBeforeFilter=2,
        totalAfterFilter=0,
    )

    monkeypatch.setattr("app.services.recommender.load_catalog", lambda: catalog)
    monkeypatch.setattr("app.services.recommender.apply_filters", lambda catalog, preferences, settings=None: empty_list)
    monkeypatch.setattr("app.services.recommender.rank_and_explain", lambda candidates, preferences, settings=None: (_ for _ in ()).throw(AssertionError("LLM should not be called")))

    response = recommend(prefs)

    assert response.summary is None
    assert response.recommendations == []
    assert response.suggestions
    assert any(
        phrase in suggestion for suggestion in response.suggestions for phrase in [
            "Try a nearby city",
            "Lower your minimum rating",
            "Choose a different cuisine",
            "Try a different budget tier",
        ]
    )
    assert response.meta is not None
    assert response.meta.candidates_considered == 0
    assert response.meta.filters_applied == ["location", "budget"]
    assert response.meta.used_fallback is False


def test_recommend_requires_location():
    prefs = UserPreferences(location="", budget="medium")
    try:
        recommend(prefs)
        assert False, "Expected ValueError for blank location"
    except ValueError as exc:
        assert "location is required" in str(exc)

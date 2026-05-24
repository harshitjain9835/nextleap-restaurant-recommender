"""Tests for LLM response parser (Phase 3)."""

import json

import pytest

from app.integration.parser import (
    build_fallback_rankings,
    extract_json_object,
    parse_llm_response,
)
from app.models import Restaurant, UserPreferences


@pytest.fixture
def candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="A",
            location="Bangalore",
            cuisine=["Italian"],
            rating=4.5,
            estimatedCost="₹800",
            budgetTier="high",
        ),
        Restaurant(
            id="r2",
            name="B",
            location="Bangalore",
            cuisine=["Chinese"],
            rating=4.0,
            estimatedCost="₹400",
            budgetTier="medium",
        ),
        Restaurant(
            id="r3",
            name="C",
            location="Bangalore",
            cuisine=["Cafe"],
            rating=3.5,
            estimatedCost="₹200",
            budgetTier="low",
        ),
    ]


@pytest.fixture
def preferences() -> UserPreferences:
    return UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")


def test_extract_json_from_markdown_fence():
    text = '```json\n{"summary": "ok", "recommendations": []}\n```'
    data = extract_json_object(text)
    assert data["summary"] == "ok"


def test_parse_valid_response(candidates, preferences):
    payload = {
        "summary": "Great picks",
        "recommendations": [
            {"restaurantId": "r1", "rank": 1, "explanation": "Best Italian spot."},
            {"restaurantId": "r2", "rank": 2, "explanation": "Solid Chinese option."},
        ],
    }
    result = parse_llm_response(json.dumps(payload), candidates, preferences, top_k=2)
    assert result.used_fallback is False
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "r1"
    assert result.summary == "Great picks"


def test_parse_drops_unknown_ids(candidates, preferences):
    payload = {
        "recommendations": [
            {"restaurantId": "fake", "rank": 1, "explanation": "Nope"},
            {"restaurantId": "r1", "rank": 2, "explanation": "Yes"},
        ]
    }
    result = parse_llm_response(json.dumps(payload), candidates, preferences, top_k=2)
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "r1"


def test_parse_backfills_to_top_k(candidates, preferences):
    payload = {
        "recommendations": [
            {"restaurantId": "r1", "rank": 1, "explanation": "Only one from LLM"},
        ]
    }
    result = parse_llm_response(json.dumps(payload), candidates, preferences, top_k=3)
    assert len(result.recommendations) == 3
    ids = {r.restaurant_id for r in result.recommendations}
    assert ids == {"r1", "r2", "r3"}


def test_parse_invalid_raises(candidates, preferences):
    with pytest.raises(ValueError):
        parse_llm_response("not json at all", candidates, preferences, top_k=2)


def test_fallback_rankings(candidates, preferences):
    result = build_fallback_rankings(candidates, preferences, top_k=2)
    assert result.used_fallback is True
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "r1"
    assert result.recommendations[0].rank == 1

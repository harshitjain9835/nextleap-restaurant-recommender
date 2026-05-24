"""Tests for LLM engine with mocked client (Phase 3)."""

import json

from app.config import Settings
from app.llm.client import LLMError
from app.llm.engine import rank_and_explain
from app.models import Restaurant, UserPreferences


class MockLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.call_count = 0

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
        json_mode: bool = True,
    ) -> str:
        if self.call_count >= len(self._responses):
            raise LLMError("No more mock responses")
        text = self._responses[self.call_count]
        self.call_count += 1
        return text


def _candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Alpha",
            location="Bangalore",
            cuisine=["Italian"],
            rating=4.6,
            estimatedCost="₹800",
            budgetTier="high",
        ),
        Restaurant(
            id="r2",
            name="Beta",
            location="Bangalore",
            cuisine=["Italian", "Pizza"],
            rating=4.2,
            estimatedCost="₹500",
            budgetTier="medium",
        ),
    ]


def test_rank_and_explain_valid_json():
    prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")
    payload = {
        "summary": "Two Italian options",
        "recommendations": [
            {"restaurantId": "r1", "rank": 1, "explanation": "Highest rating."},
            {"restaurantId": "r2", "rank": 2, "explanation": "Good value."},
        ],
    }
    client = MockLLMClient([json.dumps(payload)])
    settings = Settings.model_construct(top_k=2, llm_api_key="test")
    result = rank_and_explain(
        _candidates(), prefs, client=client, settings=settings
    )
    assert result.used_fallback is False
    assert len(result.recommendations) == 2
    assert client.call_count == 1


def test_rank_and_explain_retries_then_succeeds():
    prefs = UserPreferences(location="Bangalore", budget="medium")
    bad = "Here are my picks: not json"
    good = json.dumps(
        {
            "recommendations": [
                {"restaurantId": "r1", "rank": 1, "explanation": "Fixed."},
            ]
        }
    )
    client = MockLLMClient([bad, good])
    settings = Settings.model_construct(top_k=2, llm_api_key="test")
    result = rank_and_explain(
        _candidates(), prefs, client=client, settings=settings
    )
    assert client.call_count == 2
    assert result.recommendations[0].restaurant_id == "r1"


def test_rank_and_explain_fallback_after_two_parse_failures():
    prefs = UserPreferences(location="Bangalore", budget="medium")
    client = MockLLMClient(["not json", "still not json"])
    settings = Settings.model_construct(top_k=2, llm_api_key="test")
    result = rank_and_explain(
        _candidates(), prefs, client=client, settings=settings
    )
    assert result.used_fallback is True
    assert client.call_count == 2
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "r1"


def test_rank_and_explain_no_api_key_uses_fallback():
    prefs = UserPreferences(location="Bangalore", budget="medium")
    settings = Settings.model_construct(top_k=2, llm_api_key=None)
    result = rank_and_explain(_candidates(), prefs, settings=settings)
    assert result.used_fallback is True
    assert len(result.recommendations) == 2

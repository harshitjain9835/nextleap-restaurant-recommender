"""Tests for prompt builder (Phase 3)."""

import json

from app.integration.prompts import build_messages, build_user_prompt
from app.models import Restaurant, UserPreferences


def test_build_user_prompt_contains_candidates_and_schema():
    prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")
    candidates = [
        Restaurant(
            id="r1",
            name="Test",
            location="Bangalore",
            cuisine=["Italian"],
            rating=4.5,
            estimatedCost="₹500 for two",
            budgetTier="medium",
        )
    ]
    prompt = build_user_prompt(prefs, candidates, top_k=3)
    assert "r1" in prompt
    assert "Bangalore" in prompt
    assert "restaurantId" in prompt
    assert "Italian" in prompt


def test_build_messages_structure():
    prefs = UserPreferences(location="Bangalore", budget="low")
    messages = build_messages(prefs, [], top_k=5)
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "CANDIDATES" in messages[1]["content"]

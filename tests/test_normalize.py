"""Unit tests for dataset normalization (Phase 1)."""

import pytest

from app.config import Settings
from app.data.normalize import (
    derive_budget_tier,
    extract_city_from_address,
    parse_cost_numeric,
    parse_rating,
    row_to_restaurant,
    split_cuisines,
    stable_restaurant_id,
)


@pytest.fixture
def settings() -> Settings:
    return Settings(budget_low_max=300, budget_medium_max=600)


def test_parse_rating_valid():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("3.5/5") == 3.5


def test_parse_rating_missing_excluded():
    assert parse_rating(None) is None
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None


def test_parse_rating_clamped():
    assert parse_rating("6/5") == 5.0


def test_parse_cost_simple_and_comma():
    assert parse_cost_numeric("800") == 800
    assert parse_cost_numeric("1,000") == 1000
    assert parse_cost_numeric("300-400") == 350


def test_parse_cost_empty():
    assert parse_cost_numeric("") is None
    assert parse_cost_numeric(None) is None


def test_split_cuisines():
    assert split_cuisines("North Indian, Mughlai, Chinese") == [
        "North Indian",
        "Mughlai",
        "Chinese",
    ]
    assert split_cuisines("") == []


def test_extract_city_bangalore_aliases():
    addr = "942, 21st Main Road, 2nd Stage, Banashankari, Bangalore"
    assert extract_city_from_address(addr) == "Bangalore"
    assert extract_city_from_address("Some St, Bengaluru") == "Bangalore"


def test_extract_city_rejects_unknown_tail():
    assert extract_city_from_address("17Th E Main, Koramangala 5Th Block, 1St Stage") == ""
    assert extract_city_from_address("Shop 2, BTM, Bangalore") == "Bangalore"


def test_derive_budget_tier(settings: Settings):
    assert derive_budget_tier(200, settings) == "low"
    assert derive_budget_tier(300, settings) == "low"
    assert derive_budget_tier(500, settings) == "medium"
    assert derive_budget_tier(800, settings) == "high"


def test_stable_restaurant_id_deterministic():
    a = stable_restaurant_id("Jalsa", "Bangalore", "Banashankari", 0)
    b = stable_restaurant_id("Jalsa", "Bangalore", "Banashankari", 0)
    c = stable_restaurant_id("Jalsa", "Bangalore", "Banashankari", 1)
    assert a == b
    assert a != c
    assert a.startswith("r_")


def test_row_to_restaurant_happy_path(settings: Settings):
    row = {
        "name": "Jalsa",
        "address": "942, Banashankari, Bangalore",
        "location": "Banashankari",
        "cuisines": "North Indian, Chinese",
        "rate": "4.1/5",
        "approx_cost(for two people)": "800",
        "listed_in(city)": "Banashankari",
    }
    r = row_to_restaurant(row, 0, settings)
    assert r is not None
    assert r.name == "Jalsa"
    assert r.location == "Bangalore"
    assert r.area == "Banashankari"
    assert r.rating == 4.1
    assert r.budget_tier == "high"
    assert "North Indian" in r.cuisine
    assert r.estimated_cost.startswith("₹")


def test_row_to_restaurant_skips_missing_rating(settings: Settings):
    row = {
        "name": "No Rate Cafe",
        "address": "1 Road, Bangalore",
        "location": "Center",
        "cuisines": "Cafe",
        "rate": None,
        "approx_cost(for two people)": "300",
    }
    assert row_to_restaurant(row, 1, settings) is None


def test_row_to_restaurant_skips_missing_name(settings: Settings):
    row = {
        "name": "  ",
        "address": "1 Road, Bangalore",
        "rate": "4.0/5",
        "approx_cost(for two people)": "300",
        "cuisines": "Cafe",
    }
    assert row_to_restaurant(row, 2, settings) is None


def test_row_to_restaurant_low_budget(settings: Settings):
    row = {
        "name": "Budget Bites",
        "address": "BTM, Bangalore",
        "location": "BTM",
        "cuisines": "Fast Food",
        "rate": "3.8/5",
        "approx_cost(for two people)": "200",
    }
    r = row_to_restaurant(row, 3, settings)
    assert r is not None
    assert r.budget_tier == "low"

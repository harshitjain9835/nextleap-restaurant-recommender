"""Normalize raw Hugging Face dataset rows into Restaurant records."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from app.config import Settings
from app.models import BudgetTier, Restaurant

# Canonical city names for filtering (problem statement: Delhi, Bangalore, etc.)
_CITY_ALIASES: dict[str, str] = {
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "banglore": "Bangalore",
    "bengalore": "Bangalore",
    "btm bangalore": "Bangalore",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "ncr": "Delhi",
    "gurgaon": "Gurgaon",
    "gurugram": "Gurgaon",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "pune": "Pune",
}

_RATE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*/\s*5")
_COST_DIGITS = re.compile(r"\d+")


def canonicalize_city(raw: str | None) -> str:
    """Map a string to a canonical city only when it matches a known alias."""
    if not raw or not str(raw).strip():
        return ""
    key = str(raw).strip().lower()
    if key in _CITY_ALIASES:
        return _CITY_ALIASES[key]
    for alias, canonical in _CITY_ALIASES.items():
        if alias in key:
            return canonical
    return ""


def extract_city_from_address(address: str | None) -> str:
    """
    Find a known city in the address by scanning segments (end-first)
    and then the full address text. Unknown tails are not promoted to cities.
    """
    if not address or not str(address).strip():
        return ""
    text = str(address).strip()
    parts = [p.strip() for p in text.split(",") if p.strip()]
    for part in reversed(parts):
        city = canonicalize_city(part)
        if city:
            return city
    lower = text.lower()
    for alias, canonical in sorted(_CITY_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in lower:
            return canonical
    return ""


def parse_rating(rate: Any) -> float | None:
    """
    Parse rating from values like '4.1/5'.
    Returns None for missing/unrated rows (excluded per edge-cases DATA-05).
    """
    if rate is None:
        return None
    text = str(rate).strip()
    if not text or text.upper() in {"NEW", "-", "NAN"}:
        return None
    match = _RATE_PATTERN.search(text)
    if match:
        value = float(match.group(1))
        return max(0.0, min(5.0, value))
    try:
        value = float(text)
        return max(0.0, min(5.0, value))
    except ValueError:
        return None


def parse_cost_numeric(cost: Any) -> int | None:
    """Parse approx cost for two; handles '800', '1,000', ranges like '300-400'."""
    if cost is None:
        return None
    text = str(cost).strip()
    if not text:
        return None
    numbers = [int(n) for n in _COST_DIGITS.findall(text.replace(",", ""))]
    if not numbers:
        return None
    if len(numbers) >= 2 and "-" in text:
        return (numbers[0] + numbers[1]) // 2
    return numbers[0]


def derive_budget_tier(cost: int | None, settings: Settings) -> BudgetTier | None:
    if cost is None:
        return None
    if cost <= settings.budget_low_max:
        return "low"
    if cost <= settings.budget_medium_max:
        return "medium"
    return "high"


def split_cuisines(raw: Any) -> list[str]:
    if raw is None:
        return []
    text = str(raw).strip()
    if not text:
        return []
    parts = re.split(r"[,/|]", text)
    return [p.strip() for p in parts if p.strip()]


def stable_restaurant_id(name: str, city: str, area: str, row_index: int) -> str:
    """Stable ID for LLM join; hash with row index to avoid collisions."""
    payload = f"{name}|{city}|{area}|{row_index}".lower().encode()
    digest = hashlib.sha256(payload).hexdigest()[:12]
    return f"r_{digest}"


def format_estimated_cost(cost: int | None, raw: Any) -> str:
    if raw is not None and str(raw).strip():
        display = str(raw).strip()
        if not display.lower().startswith("₹"):
            return f"₹{display} for two"
        return display if "for two" in display.lower() else f"{display} for two"
    if cost is not None:
        return f"₹{cost:,} for two"
    return "Price not available"


def row_to_restaurant(row: dict[str, Any], row_index: int, settings: Settings) -> Restaurant | None:
    """
    Map a raw HF row to Restaurant, or None if row should be skipped.
    Skip policy: missing name, missing rating, missing city, missing budget tier.
    """
    name = str(row.get("name") or "").strip()
    if not name:
        return None

    rating = parse_rating(row.get("rate"))
    if rating is None:
        return None

    city = extract_city_from_address(row.get("address"))
    if not city:
        return None

    area = str(row.get("location") or row.get("listed_in(city)") or "").strip()
    raw_cost = row.get("approx_cost(for two people)")
    cost_num = parse_cost_numeric(raw_cost)
    budget_tier = derive_budget_tier(cost_num, settings)
    if budget_tier is None:
        return None

    cuisines = split_cuisines(row.get("cuisines"))
    restaurant_id = stable_restaurant_id(name, city, area, row_index)

    return Restaurant(
        id=restaurant_id,
        name=name,
        location=city,
        area=area,
        cuisine=cuisines,
        rating=rating,
        estimatedCost=format_estimated_cost(cost_num, raw_cost),
        budgetTier=budget_tier,
        raw={k: row[k] for k in row if k in row},
    )


def get_distinct_cities(restaurants: list[Restaurant]) -> list[str]:
    cities = sorted({r.location for r in restaurants if r.location})
    return cities

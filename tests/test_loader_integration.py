"""Optional integration test: loads real Hugging Face dataset (slow)."""

import pytest

from app.config import Settings
from app.data.loader import load_restaurants_from_hf


@pytest.mark.integration
def test_load_hf_dataset_integration():
    settings = Settings(use_parquet_cache=False)
    restaurants = load_restaurants_from_hf(settings)
    assert len(restaurants) > 1000
    sample = restaurants[0]
    assert sample.id.startswith("r_")
    assert sample.name
    assert sample.location
    assert 0 <= sample.rating <= 5
    assert sample.budget_tier in ("low", "medium", "high")

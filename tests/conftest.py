"""Pytest fixtures."""

import pytest

from app.config import Settings
from app.data import store


@pytest.fixture
def settings() -> Settings:
    return Settings(
        hf_dataset_id="ManikaSaini/zomato-restaurant-recommendation",
        budget_low_max=300,
        budget_medium_max=600,
        use_parquet_cache=False,
    )


@pytest.fixture(autouse=True)
def reset_store():
    store.reset_catalog()
    yield
    store.reset_catalog()

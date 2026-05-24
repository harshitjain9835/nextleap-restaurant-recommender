"""Unit tests for catalog store."""

from unittest.mock import patch

import pytest

from app.data.store import (
    CatalogNotLoadedError,
    get_all,
    is_catalog_loaded,
    load_catalog,
    reset_catalog,
)
from app.models import Restaurant


def _sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="r_abc",
            name="Test Place",
            location="Bangalore",
            area="Koramangala",
            cuisine=["Italian"],
            rating=4.5,
            estimatedCost="₹500 for two",
            budgetTier="medium",
        )
    ]


def test_get_all_before_load_raises():
    reset_catalog()
    with pytest.raises(CatalogNotLoadedError):
        get_all()


@patch("app.data.store.load_restaurants", return_value=_sample_restaurants())
def test_load_catalog_caches(mock_load):
    reset_catalog()
    assert not is_catalog_loaded()
    first = load_catalog()
    second = load_catalog()
    assert len(first) == 1
    assert first[0].name == "Test Place"
    assert second is first
    mock_load.assert_called_once()


@patch("app.data.store.load_restaurants", return_value=_sample_restaurants())
def test_load_catalog_force_reload(mock_load):
    reset_catalog()
    load_catalog()
    load_catalog(force_reload=True)
    assert mock_load.call_count == 2

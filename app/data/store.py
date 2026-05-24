"""In-memory restaurant catalog store (singleton)."""

from __future__ import annotations

import logging

from app.data.loader import DatasetLoadError, load_restaurants
from app.models import Restaurant

logger = logging.getLogger(__name__)

_catalog: list[Restaurant] | None = None


class CatalogNotLoadedError(Exception):
    """Raised when the catalog is accessed before load_catalog()."""


def load_catalog(force_reload: bool = False) -> list[Restaurant]:
    """
    Load and cache the normalized restaurant catalog.
    Fail fast if Hugging Face / normalization fails.
    """
    global _catalog
    if _catalog is not None and not force_reload:
        return _catalog

    logger.info("Initializing restaurant catalog...")
    _catalog = load_restaurants()
    logger.info("Catalog ready: %d restaurants", len(_catalog))
    return _catalog


def get_all() -> list[Restaurant]:
    """Return all restaurants; raises if catalog not loaded."""
    if _catalog is None:
        raise CatalogNotLoadedError(
            "Catalog not loaded. Call load_catalog() at application startup."
        )
    return list(_catalog)


def get_catalog() -> list[Restaurant]:
    """Alias for get_all(); loads catalog if not yet initialized."""
    if _catalog is None:
        return load_catalog()
    return get_all()


def get_catalog_size() -> int:
    if _catalog is None:
        return 0
    return len(_catalog)


def is_catalog_loaded() -> bool:
    return _catalog is not None


def reset_catalog() -> None:
    """Clear cached catalog (for tests)."""
    global _catalog
    _catalog = None


def get_distinct_locations() -> list[str]:
    """Canonical cities for UI dropdowns."""
    catalog = get_catalog()
    return sorted({r.location for r in catalog})


def get_distinct_areas(city: str | None = None) -> list[str]:
    """Areas/neighborhoods for a given city."""
    catalog = get_catalog()
    normalized_city = city.strip().lower() if city else None
    areas = {
        r.area
        for r in catalog
        if r.area and (normalized_city is None or r.location.strip().lower() == normalized_city)
    }
    return sorted(areas)


def get_distinct_cuisines() -> list[str]:
    """Unique cuisines across catalog."""
    catalog = get_catalog()
    seen: set[str] = set()
    for r in catalog:
        for c in r.cuisine:
            seen.add(c)
    return sorted(seen)

"""Data ingestion and restaurant catalog store."""

from app.data.store import (
    get_catalog,
    get_catalog_size,
    is_catalog_loaded,
    load_catalog,
)

__all__ = [
    "get_catalog",
    "get_catalog_size",
    "is_catalog_loaded",
    "load_catalog",
]

"""Load and preprocess the Zomato dataset from Hugging Face."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from datasets import load_dataset

from app.config import Settings, get_settings
from app.data.normalize import row_to_restaurant
from app.models import Restaurant

logger = logging.getLogger(__name__)


class DatasetLoadError(Exception):
    """Raised when the catalog cannot be loaded from Hugging Face."""


def load_raw_dataset(dataset_id: str, split: str = "train"):
    """Load dataset from Hugging Face Hub."""
    logger.info("Loading dataset %s split=%s", dataset_id, split)
    try:
        return load_dataset(dataset_id, split=split)
    except Exception as exc:
        raise DatasetLoadError(
            f"Failed to load dataset '{dataset_id}'. Check network and HF_DATASET_ID."
        ) from exc


def normalize_dataset(
    raw_rows: Any,
    settings: Settings | None = None,
) -> list[Restaurant]:
    """Convert all raw rows to normalized Restaurant records."""
    settings = settings or get_settings()
    restaurants: list[Restaurant] = []
    skipped = 0

    column_names = getattr(raw_rows, "column_names", None)
    if column_names:
        logger.info("Dataset columns: %s", column_names)

    total = len(raw_rows)
    for index in range(total):
        row = raw_rows[index]
        restaurant = row_to_restaurant(row, index, settings)
        if restaurant is None:
            skipped += 1
            continue
        restaurants.append(restaurant)

    logger.info(
        "Normalized %d restaurants (%d skipped of %d rows)",
        len(restaurants),
        skipped,
        total,
    )
    if not restaurants:
        raise DatasetLoadError("No valid restaurants after normalization.")

    return restaurants


def load_restaurants_from_hf(settings: Settings | None = None) -> list[Restaurant]:
    """Load from Hugging Face and normalize."""
    settings = settings or get_settings()
    raw = load_raw_dataset(settings.hf_dataset_id)
    return normalize_dataset(raw, settings)


def save_parquet_cache(restaurants: list[Restaurant], path: Path) -> None:
    """Persist normalized catalog for faster restarts."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    path.parent.mkdir(parents=True, exist_ok=True)
    records = [r.model_dump(by_alias=True) for r in restaurants]
    rows = []
    for r in records:
        rows.append(
            {
                "id": r["id"],
                "name": r["name"],
                "location": r["location"],
                "area": r.get("area", ""),
                "cuisine": "|".join(r.get("cuisine") or []),
                "rating": r["rating"],
                "estimatedCost": r["estimatedCost"],
                "budgetTier": r["budgetTier"],
            }
        )
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)
    logger.info("Wrote parquet cache to %s (%d rows)", path, len(rows))


def load_restaurants_from_parquet(path: Path) -> list[Restaurant]:
    """Load normalized catalog from parquet cache."""
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    restaurants: list[Restaurant] = []
    for row in table.to_pylist():
        cuisines = [c.strip() for c in str(row.get("cuisine", "")).split("|") if c.strip()]
        restaurants.append(
            Restaurant(
                id=row["id"],
                name=row["name"],
                location=row["location"],
                area=row.get("area") or "",
                cuisine=cuisines,
                rating=float(row["rating"]),
                estimatedCost=row["estimatedCost"],
                budgetTier=row["budgetTier"],
            )
        )
    return restaurants


def load_restaurants(settings: Settings | None = None) -> list[Restaurant]:
    """
    Load restaurants from parquet cache if enabled and present,
    otherwise from Hugging Face (and optionally write cache).
    """
    settings = settings or get_settings()
    cache_path = Path(settings.parquet_cache_path)

    if settings.use_parquet_cache and cache_path.is_file():
        logger.info("Loading catalog from parquet cache: %s", cache_path)
        return load_restaurants_from_parquet(cache_path)

    restaurants = load_restaurants_from_hf(settings)

    if settings.use_parquet_cache:
        try:
            save_parquet_cache(restaurants, cache_path)
        except Exception as exc:
            logger.warning("Could not write parquet cache: %s", exc)

    return restaurants

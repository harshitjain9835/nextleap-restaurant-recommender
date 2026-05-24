"""LLM recommendation engine: rank and explain a closed candidate list."""

from __future__ import annotations

import json
import logging
import time

from app.config import Settings, get_settings
from app.integration.parser import build_fallback_rankings, parse_llm_response
from app.integration.prompts import build_fix_messages, build_messages
from app.llm.client import LLMClient, LLMError, get_llm_client
from app.models import LLMRankingResult, Restaurant, UserPreferences

logger = logging.getLogger(__name__)


def rank_and_explain(
    candidates: list[Restaurant],
    preferences: UserPreferences,
    *,
    client: LLMClient | None = None,
    settings: Settings | None = None,
) -> LLMRankingResult:
    """
    Rank candidates and generate explanations via LLM.

    On parse failure: retry once with a JSON-fix prompt.
    On LLM/parse failure after retry: fallback to rating-based ranking.
    """
    settings = settings or get_settings()
    top_k = min(settings.top_k, len(candidates))

    if not candidates or top_k == 0:
        return LLMRankingResult(summary=None, recommendations=[], usedFallback=False)

    try:
        llm = client or get_llm_client(settings)
    except LLMError as exc:
        logger.warning("LLM client unavailable: %s", exc)
        return build_fallback_rankings(candidates, preferences, top_k)

    messages = build_messages(preferences, candidates, top_k)
    try:
        raw = _call_llm(llm, messages, settings)
    except LLMError as exc:
        logger.warning("LLM call failed: %s", exc)
        fallback = build_fallback_rankings(candidates, preferences, top_k)
        fallback.parse_error = str(exc)
        return fallback

    try:
        return parse_llm_response(raw, candidates, preferences, top_k)
    except (ValueError, json.JSONDecodeError) as first_err:
        logger.warning("LLM parse failed (attempt 1): %s", first_err)
        logger.debug("Raw LLM response: %s", raw[:2000])

    fix_messages = build_fix_messages(preferences, candidates, top_k, raw)
    try:
        raw_retry = _call_llm(llm, fix_messages, settings)
    except LLMError as exc:
        logger.warning("LLM call failed on retry: %s", exc)
        fallback = build_fallback_rankings(candidates, preferences, top_k)
        fallback.parse_error = str(exc)
        return fallback

    try:
        return parse_llm_response(raw_retry, candidates, preferences, top_k)
    except (ValueError, json.JSONDecodeError) as second_err:
        logger.warning("LLM parse failed (attempt 2): %s", second_err)
        logger.debug("Raw LLM retry response: %s", raw_retry[:2000])
        fallback = build_fallback_rankings(candidates, preferences, top_k)
        fallback.parse_error = str(second_err)
        return fallback


def _call_llm(
    client: LLMClient,
    messages: list[dict[str, str]],
    settings: Settings,
) -> str:
    start = time.perf_counter()
    try:
        content = client.complete(
            messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            json_mode=True,
        )
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    elapsed = time.perf_counter() - start
    logger.info("LLM call completed in %.2fs", elapsed)
    logger.debug("LLM response preview: %s", content[:500])
    return content

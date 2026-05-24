"""Domain models for the recommendation system."""

from typing import Any, Literal

from pydantic import BaseModel, Field

BudgetTier = Literal["low", "medium", "high"]


class Restaurant(BaseModel):
    """Normalized catalog record from the Zomato dataset."""

    id: str
    name: str
    location: str  # Canonical city for filtering (e.g. Bangalore)
    area: str = ""  # Neighborhood / locality for display
    cuisine: list[str] = Field(default_factory=list)
    rating: float = Field(ge=0, le=5)
    estimated_cost: str = Field(alias="estimatedCost")
    budget_tier: BudgetTier = Field(alias="budgetTier")
    raw: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}


class UserPreferences(BaseModel):
    location: str
    area: str = ""
    budget: BudgetTier
    cuisine: str = ""
    min_rating: float = Field(default=0.0, alias="minRating", ge=0, le=5)
    additional_preferences: str = Field(default="", alias="additionalPreferences")

    model_config = {"populate_by_name": True}


class CandidateList(BaseModel):
    candidates: list[Restaurant] = Field(default_factory=list)
    applied_filters: list[str] = Field(default_factory=list, alias="appliedFilters")
    total_before_filter: int = Field(alias="totalBeforeFilter")
    total_after_filter: int = Field(alias="totalAfterFilter")

    model_config = {"populate_by_name": True}


class Recommendation(BaseModel):
    restaurant_id: str = Field(alias="restaurantId")
    name: str
    cuisine: list[str]
    rating: float
    estimated_cost: str = Field(alias="estimatedCost")
    area: str | None = None
    rank: int
    explanation: str

    model_config = {"populate_by_name": True}


class RecommendationMeta(BaseModel):
    candidates_considered: int = Field(alias="candidatesConsidered")
    filters_applied: list[str] = Field(default_factory=list, alias="filtersApplied")
    used_fallback: bool = Field(default=False, alias="usedFallback")

    model_config = {"populate_by_name": True}


class RecommendationResponse(BaseModel):
    summary: str | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    meta: RecommendationMeta | None = None
    suggestions: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class LLMRecommendationItem(BaseModel):
    """Single ranked item from the LLM (IDs and text only)."""

    restaurant_id: str = Field(alias="restaurantId")
    rank: int = Field(ge=1)
    explanation: str = ""

    model_config = {"populate_by_name": True}


class LLMRankingResult(BaseModel):
    """Parsed LLM ranking output before merge with dataset fields."""

    summary: str | None = None
    recommendations: list[LLMRecommendationItem] = Field(default_factory=list)
    used_fallback: bool = Field(default=False, alias="usedFallback")
    parse_error: str | None = Field(default=None, alias="parseError")

    model_config = {"populate_by_name": True}

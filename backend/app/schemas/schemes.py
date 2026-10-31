
from typing import Any, Literal

from pydantic import BaseModel, Field


class SchemeResponse(BaseModel):
    schemeId: str | None = None
    code: str | None = None
    name: str = "Unnamed scheme"
    description: str | None = None
    state: str | None = None

    benefits: list[str] = Field(default_factory=list)
    eligibility: dict[str, Any] = Field(default_factory=dict)

    official_url: str | None = None
    source_verified_at: str | None = None

    disclaimer: str = (
        "Information is indicative. "
        "Verify with the official authority."
    )


class EligibilityRequest(BaseModel):
    state: str | None = None
    student: bool | None = None
    farmer: bool | None = None

    annual_income: float | None = Field(
        default=None,
        ge=0
    )


class EligibilityMatch(BaseModel):
    schemeId: str | None = None
    name: str
    state: str | None = None

    official_url: str | None = None
    source_verified_at: str | None = None

    status: Literal[
        "potential_match",
        "needs_more_information"
    ]

    missing_information: list[str] = Field(
        default_factory=list
    )

    disclaimer: str

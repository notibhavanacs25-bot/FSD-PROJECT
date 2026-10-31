from typing import Literal
from pydantic import BaseModel, Field


class EligibilityRequest(BaseModel):
    state: str | None = None
    age: int | None = Field(default=None, ge=0)
    annual_income: float | None = Field(default=None, ge=0)
    student: bool | None = None
    farmer: bool | None = None


class EligibilityMatch(BaseModel):
    schemeId: str | None = None
    name: str
    state: str | None = None
    official_url: str | None = None
    source_verified_at: str | None = None

    status: Literal[
        "confirmed_mismatch",
        "insufficient_information",
        "potential_match",
        "rules_require_official_verification",
    ]

    missing_information: list[str] = Field(default_factory=list)
    mismatch_reasons: list[str] = Field(default_factory=list)
    verification_reasons: list[str] = Field(default_factory=list)

    disclaimer: str

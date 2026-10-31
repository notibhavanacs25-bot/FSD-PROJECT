
import re

from fastapi import APIRouter, Query

from app.database import get_database

from app.schemas.schemes import SchemeResponse
from app.schemas.eligibility import (
    EligibilityRequest,
    EligibilityMatch,
)


router = APIRouter(
    prefix="/api/schemes",
    tags=["Government Schemes"],
)


# -------------------------------------------------
# Helper: Convert MongoDB document into API response
# -------------------------------------------------

def clean_scheme(scheme: dict) -> dict:
    return {
        "schemeId": scheme.get("schemeId"),
        "code": scheme.get("code"),
        "name": scheme.get("name", "Unnamed scheme"),
        "description": scheme.get("description"),
        "state": scheme.get("state"),
        "benefits": scheme.get("benefits", []),
        "eligibility": scheme.get("eligibility", {}),
        "official_url": scheme.get("official_url"),
        "source_verified_at": scheme.get("source_verified_at"),
        "disclaimer": scheme.get(
            "disclaimer",
            "Information is indicative. Verify with the official authority."
        ),
    }


# -------------------------------------------------
# GET ALL / SEARCH / FILTER SCHEMES
# GET /api/schemes
# GET /api/schemes?q=student
# GET /api/schemes?state=Karnataka
# -------------------------------------------------

@router.get("", response_model=list[SchemeResponse])
def get_schemes(
    q: str | None = Query(default=None, max_length=100),
    state: str | None = Query(default=None, max_length=100),
):
    db = get_database()
    collection = db["schemes"]

    search_filter = {}

    # Search by name, description, state or benefits
    if q and q.strip():
        keyword = re.escape(q.strip())

        search_filter["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}},
            {"state": {"$regex": keyword, "$options": "i"}},
            {"benefits": {"$regex": keyword, "$options": "i"}},
        ]

    # Filter by state
    if state and state.strip():
        search_filter["state"] = {
            "$regex": f"^{re.escape(state.strip())}$",
            "$options": "i",
        }

    schemes = collection.find(
        search_filter,
        {"_id": 0},
    ).sort("name", 1)

    return [clean_scheme(scheme) for scheme in schemes]


# -------------------------------------------------
# ELIGIBILITY MATCHING
# POST /api/schemes/eligibility
# -------------------------------------------------

@router.post(
    "/eligibility",
    response_model=list[EligibilityMatch],
)
def check_eligibility(user: EligibilityRequest):

    db = get_database()
    collection = db["schemes"]

    schemes = collection.find({}, {"_id": 0})

    results = []

    # Convert submitted user information into a dictionary
    user_data = user.model_dump()

    # Rules supported by this starter implementation
    supported_rules = {
        "state",
        "min_age",
        "max_age",
        "min_annual_income",
        "max_annual_income",
        "student",
        "farmer",
        "requires_official_verification",
    }

    for scheme in schemes:
        print(
            "DEBUG:",
            scheme.get("schemeId"),
            scheme.get("source_verified_at")
        )

        rules = scheme.get("eligibility") or {}

        missing_information = []
        mismatch_reasons = []
        verification_reasons = []

        # An empty eligibility dictionary is incomplete
        if not rules:
            verification_reasons.append(
                "Eligibility rules are missing or incomplete."
            )

        # Evaluate every eligibility rule
        for rule_name, rule_value in rules.items():

            # Check for unsupported rules
            if rule_name not in supported_rules:
                verification_reasons.append(
                    f"Unsupported eligibility rule: {rule_name}"
                )
                continue

            # Check official verification requirement
            if rule_name == "requires_official_verification":

                if rule_value is True:
                    verification_reasons.append(
                        "Official verification is required."
                    )

                elif rule_value is not False:
                    verification_reasons.append(
                        "Official verification requirement is unclear."
                    )

                continue

            # Check state
            if rule_name == "state":

                if not isinstance(rule_value, str) or not rule_value.strip():
                    verification_reasons.append(
                        "Scheme state requirement is incomplete."
                    )

                elif not user_data.get("state"):
                    missing_information.append("state")

                elif (
                    user_data["state"].strip().lower()
                    != rule_value.strip().lower()
                ):
                    mismatch_reasons.append(
                        f"Required state is {rule_value}."
                    )

            # Check minimum and maximum age
            elif rule_name in {"min_age", "max_age"}:

                if not isinstance(rule_value, (int, float)) or isinstance(rule_value, bool):
                    verification_reasons.append(
                        f"Invalid or incomplete rule: {rule_name}."
                    )
                    continue

                age = user_data.get("age")

                if age is None:
                    missing_information.append("age")

                elif rule_name == "min_age" and age < rule_value:
                    mismatch_reasons.append(
                        f"Minimum required age is {rule_value}."
                    )

                elif rule_name == "max_age" and age > rule_value:
                    mismatch_reasons.append(
                        f"Maximum permitted age is {rule_value}."
                    )

            # Check minimum and maximum annual income
            elif rule_name in {
                "min_annual_income",
                "max_annual_income",
            }:

                if not isinstance(rule_value, (int, float)) or isinstance(rule_value, bool):
                    verification_reasons.append(
                        f"Invalid or incomplete rule: {rule_name}."
                    )
                    continue

                income = user_data.get("annual_income")

                if income is None:
                    missing_information.append("annual_income")

                elif (
                    rule_name == "min_annual_income"
                    and income < rule_value
                ):
                    mismatch_reasons.append(
                        f"Minimum annual income required is {rule_value}."
                    )

                elif (
                    rule_name == "max_annual_income"
                    and income > rule_value
                ):
                    mismatch_reasons.append(
                        f"Maximum annual income permitted is {rule_value}."
                    )

            # Check student and farmer requirements
            elif rule_name in {"student", "farmer"}:

                if not isinstance(rule_value, bool):
                    verification_reasons.append(
                        f"Invalid or incomplete rule: {rule_name}."
                    )
                    continue

                user_value = user_data.get(rule_name)

                if user_value is None:
                    missing_information.append(rule_name)

                elif user_value != rule_value:
                    mismatch_reasons.append(
                        f"Required condition not satisfied: {rule_name}."
                    )

        # A missing verification date means the source is not verified
        if not scheme.get("source_verified_at"):
            verification_reasons.append(
                "Official source verification date is missing."
            )
        print("SCHEME ID:", scheme.get("schemeId"))
        print("SOURCE VERIFIED AT:", scheme.get("source_verified_at"))
        print("VERIFICATION REASONS:", verification_reasons)

        # Remove duplicate missing fields
        missing_information = list(dict.fromkeys(missing_information))

        # Determine final status in the required priority order
        if mismatch_reasons:
            status_text = "confirmed_mismatch"

        elif missing_information:
            status_text = "insufficient_information"

        elif verification_reasons:
            status_text = "rules_require_official_verification"

        else:
            status_text = "potential_match"
        print("FINAL STATUS:", status_text)    

        # Return every evaluated scheme
        results.append(
            EligibilityMatch(
                schemeId=scheme.get("schemeId"),
                name=scheme.get("name", "Unnamed scheme"),
                state=scheme.get("state"),
                official_url=scheme.get("official_url"),
                source_verified_at=scheme.get("source_verified_at"),
                status=status_text,
                missing_information=missing_information,
                mismatch_reasons=mismatch_reasons,
                verification_reasons=verification_reasons,
                disclaimer=(
                    "This is an indicative AI-assisted assessment, "
                    "not official eligibility or approval. "
                    "Verify all criteria with the relevant "
                    "government authority."
                ),
            )
        )

    return results

"""Pydantic response models for structured Claude API output."""

from pydantic import BaseModel


class CheckResult(BaseModel):
    """Result of a single binary rubric check."""

    check_id: str
    passed: bool
    evidence: str  # Quote from doc if failed, "" if passed
    line_hint: str  # Section/heading where issue found, "" if passed


class PersonaReviewResponse(BaseModel):
    """Structured response containing all rubric check results."""

    results: list[CheckResult]

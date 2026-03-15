"""Data models for deep validation results."""

from dataclasses import dataclass, asdict
from enum import Enum


class DeepCheckType(Enum):
    SIGNATURE_COMPLETE = "signature_complete"
    EXAMPLES_NONTRIVIAL = "examples_nontrivial"
    RETURN_TYPE_DOCUMENTED = "return_type_documented"
    SEEALSO_PRESENT = "seealso_present"
    AI_EXAMPLE_QUALITY = "ai_example_quality"


@dataclass
class DeepCheckResult:
    """Result of a single deep check on a function page."""

    check: DeepCheckType
    passed: bool
    detail: str


@dataclass
class DeepFunctionResult:
    """Aggregated deep validation result for a single function."""

    function_name: str
    doc_page: str
    file_path: str
    checks: list[DeepCheckResult]
    overall_pass: bool

    def to_dict(self) -> dict:
        d = asdict(self)
        d["checks"] = [
            {"check": c.check.value, "passed": c.passed, "detail": c.detail}
            for c in self.checks
        ]
        return d

from collections import Counter

from gauss_doc_qa.models import Finding


def build_summary(findings: list[Finding]) -> dict:
    """Build summary counts from findings list.

    Returns dict with keys:
        total: int
        by_severity: {"error": N, "warning": N, "info": N}
        by_category: {"missing_code_block": N, ...}
        by_severity_category: {"error/empty_code_block": N, ...}
    """
    by_severity = Counter(f.severity.value for f in findings)
    by_category = Counter(f.category for f in findings)
    by_severity_category = Counter(
        (f.severity.value, f.category) for f in findings
    )
    return {
        "total": len(findings),
        "by_severity": dict(by_severity),
        "by_category": dict(by_category),
        "by_severity_category": {
            f"{sev}/{cat}": count
            for (sev, cat), count in sorted(by_severity_category.items())
        },
    }

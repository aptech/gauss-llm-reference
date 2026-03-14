import json

from gauss_doc_qa.models import Finding
from gauss_doc_qa.report.summary import build_summary


def render_json(findings: list[Finding]) -> str:
    """Render findings as JSON string.

    Output format:
    {
        "summary": { ... },
        "findings": [ { file, line, severity, category, checker, message }, ... ]
    }
    """
    summary = build_summary(findings)
    output = {
        "summary": summary,
        "findings": [f.to_dict() for f in findings],
    }
    return json.dumps(output, indent=2)

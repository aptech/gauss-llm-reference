from gauss_doc_qa.models import Finding
from gauss_doc_qa.report.summary import build_summary


def render_markdown(findings: list[Finding]) -> str:
    """Render findings as Markdown string with summary header and findings table."""
    summary = build_summary(findings)
    lines = []

    # Summary header
    lines.append("# GAUSS Doc QA Report\n")
    lines.append(f"**Total findings:** {summary['total']}\n")
    lines.append("## Summary by Severity\n")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in ("error", "warning", "info"):
        count = summary["by_severity"].get(sev, 0)
        if count > 0:
            lines.append(f"| {sev.upper()} | {count} |")

    lines.append("\n## Summary by Category\n")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat, count in sorted(summary["by_category"].items()):
        lines.append(f"| {cat} | {count} |")

    if findings:
        lines.append("\n## Findings\n")
        lines.append("| Severity | File | Line | Category | Message |")
        lines.append("|----------|------|------|----------|---------|")
        for f in sorted(findings, key=lambda x: (x.severity.value, x.file)):
            line_str = str(f.line) if f.line else "-"
            lines.append(
                f"| {f.severity.value.upper()} | {f.file} | {line_str} | {f.category} | {f.message} |"
            )

    return "\n".join(lines) + "\n"

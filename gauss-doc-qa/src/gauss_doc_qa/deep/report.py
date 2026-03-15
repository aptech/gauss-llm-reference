"""Report formatters for deep validation results.

Provides terminal (Rich), JSON, and Markdown output formats for
per-function deep validation drill-down.
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from gauss_doc_qa.deep.models import DeepCheckType, DeepFunctionResult


_CHECK_LABELS = {
    DeepCheckType.SIGNATURE_COMPLETE: "Signature",
    DeepCheckType.EXAMPLES_NONTRIVIAL: "Examples",
    DeepCheckType.RETURN_TYPE_DOCUMENTED: "Return Type",
    DeepCheckType.SEEALSO_PRESENT: "See Also",
}


def render_deep_terminal(
    results: list[DeepFunctionResult],
    console: Console | None = None,
) -> None:
    """Render deep validation results as a Rich table."""
    if console is None:
        console = Console()

    total = len(results)
    passed = sum(1 for r in results if r.overall_pass)

    console.print(f"\n[bold]Deep Validation Report[/bold]")
    console.print(f"{passed}/{total} functions passed all checks\n")

    if not results:
        console.print("[green]No functions to validate.[/green]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Function", min_width=15)
    table.add_column("Signature", width=10)
    table.add_column("Examples", width=10)
    table.add_column("Return Type", width=12)
    table.add_column("See Also", width=10)
    table.add_column("Status", width=8)

    for r in results:
        check_map = {c.check: c for c in r.checks}

        def _cell(ct: DeepCheckType) -> str:
            c = check_map.get(ct)
            if c is None:
                return "-"
            return "[green]PASS[/]" if c.passed else "[red]FAIL[/]"

        status = "[bold green]PASS[/]" if r.overall_pass else "[bold red]FAIL[/]"

        table.add_row(
            r.function_name,
            _cell(DeepCheckType.SIGNATURE_COMPLETE),
            _cell(DeepCheckType.EXAMPLES_NONTRIVIAL),
            _cell(DeepCheckType.RETURN_TYPE_DOCUMENTED),
            _cell(DeepCheckType.SEEALSO_PRESENT),
            status,
        )

    console.print(table)


def render_deep_json(results: list[DeepFunctionResult]) -> str:
    """Render deep validation results as a JSON string."""
    total = len(results)
    passed = sum(1 for r in results if r.overall_pass)

    output = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
        "functions": [r.to_dict() for r in results],
    }
    return json.dumps(output, indent=2)


def render_deep_markdown(results: list[DeepFunctionResult]) -> str:
    """Render deep validation results as a Markdown string."""
    lines: list[str] = []
    total = len(results)
    passed = sum(1 for r in results if r.overall_pass)

    lines.append("# Deep Validation Report\n")
    lines.append(f"**{passed}/{total}** functions passed all deep checks\n")

    if not results:
        return "\n".join(lines) + "\n"

    # Summary table
    lines.append("| Function | Signature | Examples | Return Type | See Also | Status |")
    lines.append("|----------|-----------|----------|-------------|----------|--------|")

    for r in results:
        check_map = {c.check: c for c in r.checks}

        def _cell(ct: DeepCheckType) -> str:
            c = check_map.get(ct)
            if c is None:
                return "-"
            return "Pass" if c.passed else "FAIL"

        status = "Pass" if r.overall_pass else "FAIL"
        lines.append(
            f"| {r.function_name} | {_cell(DeepCheckType.SIGNATURE_COMPLETE)} "
            f"| {_cell(DeepCheckType.EXAMPLES_NONTRIVIAL)} "
            f"| {_cell(DeepCheckType.RETURN_TYPE_DOCUMENTED)} "
            f"| {_cell(DeepCheckType.SEEALSO_PRESENT)} "
            f"| {status} |"
        )

    # Failed functions detail section
    failed = [r for r in results if not r.overall_pass]
    if failed:
        lines.append("")
        lines.append("## Failed Functions\n")
        for r in failed:
            lines.append(f"### {r.function_name}\n")
            for c in r.checks:
                if not c.passed:
                    label = _CHECK_LABELS.get(c.check, c.check.value)
                    lines.append(f"- **{label}:** {c.detail}")
            lines.append("")

    return "\n".join(lines) + "\n"

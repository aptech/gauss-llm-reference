from rich.console import Console
from rich.table import Table

from gauss_doc_qa.models import Finding, Severity
from gauss_doc_qa.report.summary import build_summary

SEVERITY_COLORS = {
    Severity.ERROR: "red",
    Severity.WARNING: "yellow",
    Severity.INFO: "blue",
}


def render_terminal(findings: list[Finding], console: Console | None = None) -> None:
    if console is None:
        console = Console()

    summary = build_summary(findings)

    # Summary header
    console.print(f"\n[bold]GAUSS Doc QA Report[/bold]")
    console.print(f"Total findings: {summary['total']}")
    for sev in ("error", "warning", "info"):
        count = summary["by_severity"].get(sev, 0)
        if count > 0:
            color = {"error": "red", "warning": "yellow", "info": "blue"}[sev]
            console.print(f"  [{color}]{sev.upper()}: {count}[/{color}]")

    if not findings:
        console.print("\n[green]No issues found.[/green]")
        return

    # Findings table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Severity", width=8)
    table.add_column("File", min_width=20)
    table.add_column("Line", width=6)
    table.add_column("Category", min_width=15)
    table.add_column("Message", min_width=30)

    for f in sorted(findings, key=lambda x: (x.severity.value, x.file)):
        color = SEVERITY_COLORS[f.severity]
        table.add_row(
            f"[{color}]{f.severity.value.upper()}[/{color}]",
            f.file,
            str(f.line) if f.line else "-",
            f.category,
            f.message,
        )

    console.print(table)

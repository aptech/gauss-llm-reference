"""Report formatters for frequency ranking output.

Provides terminal (Rich), JSON, and Markdown renderers for
ranked FunctionFrequency lists.
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from gauss_doc_qa.frequency.models import FunctionFrequency


def _apply_top_n(
    rankings: list[FunctionFrequency], top_n: int | None
) -> list[FunctionFrequency]:
    """Slice rankings to top_n if set."""
    if top_n is not None:
        return rankings[:top_n]
    return rankings


def render_frequency_terminal(
    rankings: list[FunctionFrequency],
    top_n: int | None = None,
    console: Console | None = None,
) -> None:
    """Render frequency rankings as a Rich table to the console.

    Args:
        rankings: Sorted list of FunctionFrequency entries.
        top_n: If set, only show the top N entries.
        console: Optional Rich Console (defaults to new Console).
    """
    if console is None:
        console = Console()

    display = _apply_top_n(rankings, top_n)

    console.print(f"\n[bold]GAUSS Function Frequency Ranking[/bold]")
    console.print(f"Total functions: {len(rankings)}")
    if top_n is not None:
        console.print(f"Showing: top {top_n}")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Rank", width=6)
    table.add_column("Function", min_width=20)
    table.add_column("Doc Refs", width=10)
    table.add_column("Blog Mentions", width=14)
    table.add_column("Combined Score", width=14)

    for i, entry in enumerate(display, start=1):
        table.add_row(
            str(i),
            entry.name,
            str(entry.doc_refs),
            str(entry.blog_mentions),
            f"{entry.combined_score:.1f}",
        )

    console.print(table)


def render_frequency_json(
    rankings: list[FunctionFrequency],
    top_n: int | None = None,
) -> str:
    """Render frequency rankings as a JSON string.

    Args:
        rankings: Sorted list of FunctionFrequency entries.
        top_n: If set, only include the top N entries.

    Returns:
        JSON string with total_functions, top_n, and rankings array.
    """
    display = _apply_top_n(rankings, top_n)

    output = {
        "total_functions": len(rankings),
        "top_n": top_n,
        "rankings": [
            {
                "rank": i,
                "name": entry.name,
                "doc_refs": entry.doc_refs,
                "blog_mentions": entry.blog_mentions,
                "combined_score": entry.combined_score,
            }
            for i, entry in enumerate(display, start=1)
        ],
    }
    return json.dumps(output, indent=2)


def render_frequency_markdown(
    rankings: list[FunctionFrequency],
    top_n: int | None = None,
) -> str:
    """Render frequency rankings as a Markdown string.

    Args:
        rankings: Sorted list of FunctionFrequency entries.
        top_n: If set, only include the top N entries.

    Returns:
        Markdown string with header, summary, and rankings table.
    """
    display = _apply_top_n(rankings, top_n)
    lines: list[str] = []

    lines.append("# GAUSS Function Frequency Ranking\n")
    lines.append(f"**Total functions:** {len(rankings)}\n")
    if top_n is not None:
        lines.append(f"**Showing:** top {top_n}\n")

    lines.append("| Rank | Function | Doc Refs | Blog Mentions | Combined Score |")
    lines.append("|------|----------|----------|---------------|----------------|")

    for i, entry in enumerate(display, start=1):
        lines.append(
            f"| {i} | {entry.name} | {entry.doc_refs} | {entry.blog_mentions} | {entry.combined_score:.1f} |"
        )

    return "\n".join(lines) + "\n"

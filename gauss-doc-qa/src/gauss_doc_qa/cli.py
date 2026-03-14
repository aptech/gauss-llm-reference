"""GAUSS Documentation QA CLI.

Provides ``gauss-qa`` command with ``scan`` and ``inventory`` subcommands.
"""

import click
from pathlib import Path
from rich.console import Console

from gauss_doc_qa.parser.inventory import scan_docs_dir, load_exclude_patterns
from gauss_doc_qa.parser.rst_parser import parse_rst
from gauss_doc_qa.checkers import get_all_fast_checkers, get_checker
from gauss_doc_qa.report.terminal import render_terminal
from gauss_doc_qa.report.json_report import render_json
from gauss_doc_qa.report.markdown_report import render_markdown


@click.group()
@click.option("--docs-dir", type=click.Path(exists=True), required=True,
              help="Path to Sphinx docs directory")
@click.pass_context
def cli(ctx, docs_dir):
    """GAUSS Documentation QA Tool"""
    ctx.ensure_object(dict)
    ctx.obj["docs_dir"] = str(Path(docs_dir).resolve())


@cli.command()
@click.option("--format", "output_format",
              type=click.Choice(["terminal", "json", "markdown"]),
              default="terminal", help="Output format")
@click.option("--check", "checker_name", type=str, default=None,
              help="Run specific checker only (e.g., code_blocks, sections, signatures)")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write report to file instead of stdout")
@click.pass_context
def scan(ctx, output_format, checker_name, output):
    """Run structural checks on all RST files."""
    docs_dir = ctx.obj["docs_dir"]

    # Discover files
    conf_py = Path(docs_dir) / "conf.py"
    exclude = load_exclude_patterns(str(conf_py)) if conf_py.exists() else None
    file_list = scan_docs_dir(docs_dir, exclude)

    # Select checkers
    if checker_name:
        checkers = [get_checker(checker_name)]
    else:
        checkers = get_all_fast_checkers()

    # Parse and check
    all_findings = []
    for filepath, doc_type in file_list:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        parsed = parse_rst(filepath, content, doc_type)
        for checker in checkers:
            findings = checker.check(parsed)
            all_findings.extend(findings)

    # Render
    if output_format == "json":
        report_text = render_json(all_findings)
        if output:
            Path(output).write_text(report_text)
        else:
            click.echo(report_text)
    elif output_format == "markdown":
        report_text = render_markdown(all_findings)
        if output:
            Path(output).write_text(report_text)
        else:
            click.echo(report_text)
    else:
        # terminal format
        if output:
            with open(output, "w") as f:
                console = Console(file=f, force_terminal=False)
                render_terminal(all_findings, console)
        else:
            console = Console()
            render_terminal(all_findings, console)


@cli.command()
@click.pass_context
def inventory(ctx):
    """List all RST files with their doc type classification."""
    docs_dir = ctx.obj["docs_dir"]
    conf_py = Path(docs_dir) / "conf.py"
    exclude = load_exclude_patterns(str(conf_py)) if conf_py.exists() else None
    file_list = scan_docs_dir(docs_dir, exclude)

    console = Console()
    from rich.table import Table
    table = Table(show_header=True, header_style="bold")
    table.add_column("File", min_width=30)
    table.add_column("Doc Type", min_width=15)

    for filepath, doc_type in file_list:
        rel_path = str(Path(filepath).relative_to(docs_dir))
        table.add_row(rel_path, doc_type.value)

    console.print(f"\nTotal RST files: {len(file_list)}")
    console.print(table)

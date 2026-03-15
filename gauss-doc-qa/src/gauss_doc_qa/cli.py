"""GAUSS Documentation QA CLI.

Provides ``gauss-qa`` command with ``scan``, ``check-refs``, and ``inventory`` subcommands.
"""

import click
from pathlib import Path
from rich.console import Console

from gauss_doc_qa.parser.inventory import scan_docs_dir, load_exclude_patterns
from gauss_doc_qa.parser.rst_parser import parse_rst
from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
from gauss_doc_qa.checkers import get_all_fast_checkers, get_all_sphinx_checkers, get_checker
from gauss_doc_qa.report.terminal import render_terminal
from gauss_doc_qa.report.json_report import render_json
from gauss_doc_qa.report.markdown_report import render_markdown


def _render_findings(all_findings, output_format, output):
    """Shared rendering logic for scan and check-refs commands."""
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
@click.option("--sphinx", is_flag=True, default=False,
              help="Also run Sphinx-mode checks (cross-refs, orphans, coverage, seealso)")
@click.pass_context
def scan(ctx, output_format, checker_name, output, sphinx):
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
    parsed_docs = []
    all_code_blocks = {}
    for filepath, doc_type in file_list:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        parsed = parse_rst(filepath, content, doc_type)
        parsed_docs.append(parsed)
        all_code_blocks[parsed.path] = [cb.content for cb in parsed.code_blocks]
        for checker in checkers:
            findings = checker.check(parsed)
            all_findings.extend(findings)

    # Run sphinx-mode checks if requested
    if sphinx:
        click.echo("Loading Sphinx environment...")
        env = load_sphinx_env(docs_dir)
        click.echo(f"Sphinx environment loaded: {len(env.all_docs)} documents")

        sphinx_checkers = get_all_sphinx_checkers()
        for parsed in parsed_docs:
            for checker in sphinx_checkers:
                findings = checker.check(parsed, sphinx_env=env, all_code_blocks=all_code_blocks)
                all_findings.extend(findings)

    # Render
    _render_findings(all_findings, output_format, output)


@cli.command("check-refs")
@click.option("--format", "output_format",
              type=click.Choice(["terminal", "json", "markdown"]),
              default="terminal", help="Output format")
@click.option("--check", "checker_name", type=str, default=None,
              help="Run specific sphinx checker (links, orphans, coverage, seealso)")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write report to file")
@click.pass_context
def check_refs(ctx, output_format, checker_name, output):
    """Run cross-reference validation checks (requires Sphinx environment)."""
    docs_dir = ctx.obj["docs_dir"]

    # Load Sphinx environment
    click.echo("Loading Sphinx environment...")
    env = load_sphinx_env(docs_dir)
    click.echo(f"Sphinx environment loaded: {len(env.all_docs)} documents")

    # Parse all files for code blocks (needed by coverage checker)
    conf_py = Path(docs_dir) / "conf.py"
    exclude = load_exclude_patterns(str(conf_py)) if conf_py.exists() else None
    file_list = scan_docs_dir(docs_dir, exclude)

    all_code_blocks = {}
    parsed_docs = []
    for filepath, doc_type in file_list:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        parsed = parse_rst(filepath, content, doc_type)
        parsed_docs.append(parsed)
        all_code_blocks[parsed.path] = [cb.content for cb in parsed.code_blocks]

    # Select checkers
    if checker_name:
        checkers = [get_checker(checker_name)]
    else:
        checkers = get_all_sphinx_checkers()

    # Run checks
    all_findings = []
    for parsed in parsed_docs:
        for checker in checkers:
            findings = checker.check(parsed, sphinx_env=env, all_code_blocks=all_code_blocks)
            all_findings.extend(findings)

    # Render
    _render_findings(all_findings, output_format, output)


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

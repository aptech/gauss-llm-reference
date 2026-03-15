"""GAUSS Documentation QA CLI.

Provides ``gauss-qa`` command with ``scan``, ``check-refs``, and ``inventory`` subcommands.
"""

import click
from pathlib import Path
from rich.console import Console

from gauss_doc_qa.parser.inventory import scan_docs_dir, load_exclude_patterns
from gauss_doc_qa.parser.rst_parser import parse_rst
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
        from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
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
    from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
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


@cli.command()
@click.option("--apply", is_flag=True, default=False,
              help="Apply fixes (default is dry-run)")
@click.option("--verify", is_flag=True, default=False,
              help="Run Sphinx build verification after applying fixes")
@click.option("--min-confidence", type=float, default=0.85,
              help="Minimum fuzzy match confidence for auto-fix")
@click.pass_context
def fix(ctx, apply, verify, min_confidence):
    """Auto-fix broken internal links (dry-run by default)."""
    docs_dir = ctx.obj["docs_dir"]

    # Load Sphinx environment (lazy import, same pattern as check-refs)
    from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
    from gauss_doc_qa.fixer import resolve_fixes, apply_fixes, verify_sphinx_build

    click.echo("Loading Sphinx environment...")
    env = load_sphinx_env(docs_dir)
    click.echo(f"Sphinx environment loaded: {len(env.all_docs)} documents")

    # Parse all RST files
    conf_py = Path(docs_dir) / "conf.py"
    exclude = load_exclude_patterns(str(conf_py)) if conf_py.exists() else None
    file_list = scan_docs_dir(docs_dir, exclude)

    parsed_docs = []
    all_code_blocks = {}
    for filepath, doc_type in file_list:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        parsed = parse_rst(filepath, content, doc_type)
        parsed_docs.append(parsed)
        all_code_blocks[parsed.path] = [cb.content for cb in parsed.code_blocks]

    # Run LinksChecker and SeeAlsoChecker to find broken refs
    from gauss_doc_qa.checkers import get_checker
    links_checker = get_checker("links")
    seealso_checker = get_checker("seealso")

    all_findings = []
    for parsed in parsed_docs:
        for checker in [links_checker, seealso_checker]:
            findings = checker.check(parsed, sphinx_env=env, all_code_blocks=all_code_blocks)
            all_findings.extend(findings)

    # Resolve fixable findings into proposals
    gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})
    proposals = resolve_fixes(all_findings, gauss_objects, min_confidence)

    if not proposals:
        click.echo("No auto-fixable issues found.")
        return

    # Apply (dry-run or real)
    applied = apply_fixes(proposals, dry_run=not apply)

    # Render output with Rich
    console = Console(no_color=False)
    for proposal in applied:
        console.print(f"--- {proposal.file_path} (line {proposal.line_number})")
        console.print(f"- {proposal.original_text}", style="red")
        console.print(f"+ {proposal.fixed_text}", style="green")
        console.print(
            f"  [confidence: {proposal.confidence:.2f}, category: {proposal.category}]"
        )
        console.print()

    # Summary line with confidence breakdown
    high = sum(1 for p in applied if p.confidence >= 0.95)
    medium = sum(1 for p in applied if 0.85 <= p.confidence < 0.95)
    click.echo(
        f"Proposed fixes: {len(applied)} ({high} high confidence, {medium} medium)"
    )

    if not apply:
        click.echo("Run with --apply to write changes.")
    else:
        click.echo(f"Applied {len(applied)} fixes.")

    # Verification
    if verify and apply:
        click.echo("Running Sphinx build verification...")
        result = verify_sphinx_build(docs_dir)
        status = "PASSED" if result["success"] else "FAILED"
        click.echo(
            f"Verification: {status} ({result['warning_count']} warnings)"
        )
    elif verify and not apply:
        click.echo("Skipping --verify (no changes applied).")

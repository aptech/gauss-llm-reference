"""GAUSS Documentation QA CLI.

Provides ``gauss-qa`` command with ``scan``, ``check-refs``, ``review``, and ``inventory`` subcommands.
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
@click.option("--glossary", type=click.Path(exists=True), default=None,
              help="Path to YAML glossary file for terminology checking")
@click.pass_context
def scan(ctx, output_format, checker_name, output, sphinx, glossary):
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

    # Run glossary checker if --glossary provided
    if glossary:
        from gauss_doc_qa.glossary import load_glossary
        from gauss_doc_qa.checkers.glossary import GlossaryChecker

        glossary_entries = load_glossary(glossary)
        glossary_checker = GlossaryChecker(glossary_entries)

        for parsed in parsed_docs:
            findings = glossary_checker.check(parsed)
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


@cli.command()
@click.option("--persona", type=click.Choice(["newcomer", "expert", "writer", "all"]),
              default="all", help="Which persona to run")
@click.option("--sample", type=int, default=20,
              help="Number of Command Reference pages to sample for expert persona")
@click.option("--format", "output_format",
              type=click.Choice(["terminal", "json", "markdown"]),
              default="terminal", help="Output format")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write report to file")
@click.pass_context
def review(ctx, persona, sample, output_format, output):
    """Run AI persona reviews on documentation."""
    import os
    import random

    docs_dir = ctx.obj["docs_dir"]

    # Check for API key before doing anything
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise click.ClickException(
            "ANTHROPIC_API_KEY environment variable is required for AI reviews. "
            "Set it with: export ANTHROPIC_API_KEY=your-key-here"
        )

    # Lazy imports
    from gauss_doc_qa.ai.checker import AIPersonaChecker
    from gauss_doc_qa.ai.personas import PERSONAS
    from gauss_doc_qa.models import DocType

    # Discover and parse files
    conf_py = Path(docs_dir) / "conf.py"
    exclude = load_exclude_patterns(str(conf_py)) if conf_py.exists() else None
    file_list = scan_docs_dir(docs_dir, exclude)

    # Determine which personas to run
    if persona == "all":
        active_personas = list(PERSONAS.values())
    else:
        active_personas = [PERSONAS[persona]]

    # Filter files to only those matching persona target doc types
    target_types = set()
    for p in active_personas:
        target_types.update(p.target_doc_types)

    matching_files = [(fp, dt) for fp, dt in file_list if dt in target_types]

    # For expert persona, sample Command Reference pages
    if DocType.COMMAND_REF in target_types:
        cmd_ref_files = [(fp, dt) for fp, dt in matching_files if dt == DocType.COMMAND_REF]
        other_files = [(fp, dt) for fp, dt in matching_files if dt != DocType.COMMAND_REF]
        if len(cmd_ref_files) > sample:
            cmd_ref_files = random.sample(cmd_ref_files, sample)
        matching_files = other_files + cmd_ref_files

    # Parse and review with progress
    from rich.progress import Progress

    all_findings = []

    with Progress() as progress:
        task = progress.add_task("Reviewing docs...", total=len(matching_files) * len(active_personas))
        for filepath, doc_type in matching_files:
            content = Path(filepath).read_text(encoding="utf-8", errors="replace")
            parsed = parse_rst(filepath, content, doc_type)
            for p in active_personas:
                if doc_type in p.target_doc_types:
                    from gauss_doc_qa.ai.reviewer import run_persona_review
                    findings = run_persona_review(parsed, p)
                    all_findings.extend(findings)
                progress.advance(task)

    # Render
    _render_findings(all_findings, output_format, output)

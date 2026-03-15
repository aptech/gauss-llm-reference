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
@click.option("--glossary", type=click.Path(exists=True), default=None,
              help="Path to YAML glossary file for terminology auto-fix")
@click.pass_context
def fix(ctx, apply, verify, min_confidence, glossary):
    """Auto-fix broken internal links and terminology (dry-run by default)."""
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

    # Resolve fixable findings into proposals (pass doc_names and label_names)
    gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})
    doc_names = list(env.all_docs.keys())
    std_labels = env.domaindata.get("std", {}).get("labels", {})
    label_names = list(std_labels.keys())
    proposals = resolve_fixes(
        all_findings, gauss_objects, min_confidence,
        doc_names=doc_names, label_names=label_names,
    )

    # Handle glossary fixes when --glossary provided
    if glossary:
        from gauss_doc_qa.glossary import load_glossary
        from gauss_doc_qa.checkers.glossary import GlossaryChecker
        from gauss_doc_qa.fixer import resolve_glossary_fixes

        glossary_entries = load_glossary(glossary)
        glossary_checker = GlossaryChecker(glossary_entries)

        glossary_findings = []
        for parsed in parsed_docs:
            glossary_findings.extend(glossary_checker.check(parsed))

        glossary_proposals = resolve_glossary_fixes(glossary_findings, glossary_entries)
        proposals.extend(glossary_proposals)

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
@click.option("--top-n", type=int, default=None,
              help="Show only top N functions (default: show all)")
@click.option("--format", "output_format",
              type=click.Choice(["terminal", "json", "markdown"]),
              default="terminal", help="Output format")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write report to file instead of stdout")
@click.option("--output-targets", type=click.Path(), default=None,
              help="Write top-N function names to file (one per line) for deep validation")
@click.option("--no-blog", is_flag=True, default=False,
              help="Skip blog scraping (offline/fast mode)")
@click.option("--doc-weight", type=float, default=0.7,
              help="Weight for doc cross-reference count (default: 0.7)")
@click.option("--blog-weight", type=float, default=0.3,
              help="Weight for blog mention count (default: 0.3)")
@click.pass_context
def freq(ctx, top_n, output_format, output, output_targets, no_blog, doc_weight, blog_weight):
    """Rank Command Reference functions by cross-reference frequency."""
    docs_dir = ctx.obj["docs_dir"]

    # Load Sphinx env (lazy import, same as check-refs)
    from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
    click.echo("Loading Sphinx environment...")
    env = load_sphinx_env(docs_dir)
    click.echo(f"Sphinx environment loaded: {len(env.all_docs)} documents")

    # Count doc cross-references
    from gauss_doc_qa.frequency.counter import count_crossrefs
    click.echo("Counting cross-references...")
    doc_ref_counts = count_crossrefs(docs_dir, env)

    # Scrape blog mentions (unless --no-blog)
    blog_mention_counts: dict[str, int] = {}
    if not no_blog:
        from gauss_doc_qa.frequency.blog_scraper import scrape_blog_mentions
        known_functions = set(env.domaindata.get("gauss", {}).get("objects", {}).keys())
        click.echo(f"Scraping blog mentions for {len(known_functions)} functions...")
        blog_mention_counts = scrape_blog_mentions(known_functions)
        click.echo(f"Found blog mentions for {len([v for v in blog_mention_counts.values() if v > 0])} functions")
    else:
        click.echo("Skipping blog scraping (--no-blog)")

    # Rank functions
    from gauss_doc_qa.frequency.scorer import rank_functions
    rankings = rank_functions(env, doc_ref_counts, blog_mention_counts, doc_weight, blog_weight)
    click.echo(f"Ranked {len(rankings)} functions")

    # Apply top_n default of 100 for --output-targets if top_n not explicitly set
    targets_n = top_n if top_n is not None else 100

    # Write target list file if requested
    if output_targets:
        target_names = [r.name for r in rankings[:targets_n]]
        Path(output_targets).write_text("\n".join(target_names) + "\n")
        click.echo(f"Wrote {len(target_names)} target function names to {output_targets}")

    # Render report
    from gauss_doc_qa.frequency.report import (
        render_frequency_terminal, render_frequency_json, render_frequency_markdown
    )

    if output_format == "json":
        report_text = render_frequency_json(rankings, top_n)
        if output:
            Path(output).write_text(report_text)
        else:
            click.echo(report_text)
    elif output_format == "markdown":
        report_text = render_frequency_markdown(rankings, top_n)
        if output:
            Path(output).write_text(report_text)
        else:
            click.echo(report_text)
    else:
        if output:
            with open(output, "w") as f:
                console = Console(file=f, force_terminal=False)
                render_frequency_terminal(rankings, top_n, console)
        else:
            render_frequency_terminal(rankings, top_n)


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


@cli.command("deep-validate")
@click.option("--top-n", type=int, default=100,
              help="Number of top functions to validate (default: 100)")
@click.option("--targets-file", type=click.Path(exists=True), default=None,
              help="File with function names (one per line), e.g., from freq --output-targets")
@click.option("--no-ai", is_flag=True, default=False,
              help="Skip AI-assisted example verification (faster, structural checks only)")
@click.option("--no-blog", is_flag=True, default=False,
              help="Skip blog scraping when computing frequency ranking")
@click.option("--format", "output_format",
              type=click.Choice(["terminal", "json", "markdown"]),
              default="terminal", help="Output format")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write report to file instead of stdout")
@click.pass_context
def deep_validate(ctx, top_n, targets_file, no_ai, no_blog, output_format, output):
    """Deep validation of top-N function pages."""
    import os

    docs_dir = ctx.obj["docs_dir"]

    # Step 1: Determine target function names
    if targets_file:
        # Read from targets file (one name per line)
        target_names = [
            line.strip()
            for line in Path(targets_file).read_text().strip().split("\n")
            if line.strip()
        ]
        click.echo(f"Loaded {len(target_names)} target functions from {targets_file}")
    else:
        # Run frequency ranking pipeline to determine top-N
        from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
        click.echo("Loading Sphinx environment...")
        env = load_sphinx_env(docs_dir)
        click.echo(f"Sphinx environment loaded: {len(env.all_docs)} documents")

        from gauss_doc_qa.frequency.counter import count_crossrefs
        click.echo("Counting cross-references...")
        doc_ref_counts = count_crossrefs(docs_dir, env)

        blog_mention_counts: dict[str, int] = {}
        if not no_blog:
            from gauss_doc_qa.frequency.blog_scraper import scrape_blog_mentions
            known_functions = set(env.domaindata.get("gauss", {}).get("objects", {}).keys())
            click.echo(f"Scraping blog mentions for {len(known_functions)} functions...")
            blog_mention_counts = scrape_blog_mentions(known_functions)
        else:
            click.echo("Skipping blog scraping (--no-blog)")

        from gauss_doc_qa.frequency.scorer import rank_functions
        rankings = rank_functions(env, doc_ref_counts, blog_mention_counts, 0.7, 0.3)
        target_names = [r.name for r in rankings[:top_n]]
        click.echo(f"Selected top {len(target_names)} functions by frequency")

    # Step 2: Load Sphinx environment (if not already loaded)
    if targets_file:
        from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
        click.echo("Loading Sphinx environment...")
        env = load_sphinx_env(docs_dir)
        click.echo(f"Sphinx environment loaded: {len(env.all_docs)} documents")

    # Step 3: Run structural deep checks
    from gauss_doc_qa.deep.checker import deep_check_functions
    click.echo(f"Running structural deep checks on {len(target_names)} functions...")
    results = deep_check_functions(target_names, docs_dir, env)
    click.echo(f"Checked {len(results)} functions (some targets may not have doc pages)")

    # Step 4: Run AI checks (unless --no-ai)
    if not no_ai:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            click.echo("Warning: ANTHROPIC_API_KEY not set, skipping AI checks. Use --no-ai to suppress this warning.")
        else:
            from gauss_doc_qa.deep.ai_checker import ai_check_examples_batch
            click.echo("Running AI example verification...")
            results = ai_check_examples_batch(results, docs_dir)
    else:
        click.echo("Skipping AI checks (--no-ai)")

    # Step 5: Render report
    from gauss_doc_qa.deep.report import render_deep_terminal, render_deep_json, render_deep_markdown

    if output_format == "json":
        report_text = render_deep_json(results)
        if output:
            Path(output).write_text(report_text)
        else:
            click.echo(report_text)
    elif output_format == "markdown":
        report_text = render_deep_markdown(results)
        if output:
            Path(output).write_text(report_text)
        else:
            click.echo(report_text)
    else:
        if output:
            with open(output, "w") as f:
                console = Console(file=f, force_terminal=False)
                render_deep_terminal(results, console)
        else:
            render_deep_terminal(results)

    # Step 6: Summary line
    passed = sum(1 for r in results if r.overall_pass)
    click.echo(f"Deep validation: {passed}/{len(results)} functions passed all checks")

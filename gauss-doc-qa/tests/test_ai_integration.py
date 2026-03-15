"""Integration tests for AI findings flowing through the report pipeline."""

import json
from io import StringIO
from pathlib import Path

import pytest
from click.testing import CliRunner
from rich.console import Console

from gauss_doc_qa.models import Finding, Severity, DocType, ParsedDoc, CodeBlock
from gauss_doc_qa.report.terminal import render_terminal
from gauss_doc_qa.report.json_report import render_json
from gauss_doc_qa.report.markdown_report import render_markdown


def _make_ai_findings():
    """Create sample AI findings for testing."""
    return [
        Finding(
            file="getting_started/intro.rst",
            line=None,
            severity=Severity.ERROR,
            category="missing_prerequisite",
            checker="ai_newcomer",
            message="[NEW-04] Are prerequisite steps mentioned? -- No install instructions",
            auto_fixable=False,
        ),
        Finding(
            file="commands/plotxy.rst",
            line=None,
            severity=Severity.WARNING,
            category="missing_return_type",
            checker="ai_expert",
            message="[EXP-03] Is the return type documented? -- No return section found",
            auto_fixable=False,
        ),
    ]


def _make_structural_findings():
    """Create sample structural findings for testing."""
    return [
        Finding(
            file="commands/ols.rst",
            line=15,
            severity=Severity.ERROR,
            category="missing_code_block",
            checker="code_blocks",
            message="Command Reference page has no code examples",
            auto_fixable=False,
        ),
        Finding(
            file="commands/abs.rst",
            line=3,
            severity=Severity.WARNING,
            category="missing_section",
            checker="sections",
            message="Missing required section: Purpose",
            auto_fixable=False,
        ),
    ]


class TestAIFindingsInTerminalReport:

    def test_ai_findings_in_terminal_report(self):
        findings = _make_ai_findings()
        buf = StringIO()
        console = Console(no_color=True, file=buf, width=200)
        render_terminal(findings, console)
        output = buf.getvalue()

        # Terminal table shows Severity, File, Line, Category, Message
        assert "ERROR" in output
        assert "WARNING" in output
        assert "missing_prerequisite" in output or "missing_prerequ" in output
        assert "missing_return_type" in output or "missing_return_" in output
        # AI findings should render without errors
        assert "NEW-04" in output
        assert "EXP-03" in output


class TestAIFindingsInJsonReport:

    def test_ai_findings_in_json_report(self):
        findings = _make_ai_findings()
        report_text = render_json(findings)
        data = json.loads(report_text)

        assert "summary" in data
        assert "findings" in data
        assert len(data["findings"]) == 2

        checkers = {f["checker"] for f in data["findings"]}
        assert "ai_newcomer" in checkers
        assert "ai_expert" in checkers

        # Verify standard Finding schema
        for f in data["findings"]:
            assert "file" in f
            assert "severity" in f
            assert "category" in f
            assert "checker" in f
            assert "message" in f

        # Verify severity values
        severities = {f["severity"] for f in data["findings"]}
        assert "error" in severities
        assert "warning" in severities


class TestAIFindingsInMarkdownReport:

    def test_ai_findings_in_markdown_report(self):
        findings = _make_ai_findings()
        output = render_markdown(findings)

        # Markdown table has Severity, File, Line, Category, Message columns
        assert "ERROR" in output
        assert "WARNING" in output
        assert "missing_prerequisite" in output
        assert "missing_return_type" in output
        assert "NEW-04" in output
        assert "EXP-03" in output
        # Should be valid markdown table
        assert "| Severity |" in output


class TestAIFindingsMixedWithStructural:

    def test_ai_findings_mixed_with_structural(self):
        ai_findings = _make_ai_findings()
        structural_findings = _make_structural_findings()
        mixed = ai_findings + structural_findings

        # Terminal (checker name not shown in table, check categories/messages)
        buf = StringIO()
        console = Console(no_color=True, file=buf, width=200)
        render_terminal(mixed, console)
        terminal_output = buf.getvalue()
        assert "NEW-04" in terminal_output
        assert "EXP-03" in terminal_output
        assert "missing_code_block" in terminal_output
        assert "missing_section" in terminal_output

        # JSON
        json_output = render_json(mixed)
        data = json.loads(json_output)
        assert len(data["findings"]) == 4
        checkers = {f["checker"] for f in data["findings"]}
        assert checkers == {"ai_newcomer", "ai_expert", "code_blocks", "sections"}

        # Markdown (checker name not in table, check categories/messages)
        md_output = render_markdown(mixed)
        assert "NEW-04" in md_output
        assert "EXP-03" in md_output
        assert "missing_code_block" in md_output
        assert "missing_section" in md_output


class TestReviewCLIMissingApiKey:

    def test_review_cli_missing_api_key(self):
        from gauss_doc_qa.cli import cli

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--docs-dir", str(Path(__file__).parent / "fixtures"), "review"],
            env={"ANTHROPIC_API_KEY": ""},
        )
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output


class TestAICheckerSkipsWrongDocType:

    def test_ai_checker_skips_wrong_doc_type(self):
        from gauss_doc_qa.ai.checker import AIPersonaChecker

        checker = AIPersonaChecker()

        # Create a ParsedDoc with ALPHA_INDEX doc type (no persona targets this)
        parsed = ParsedDoc(
            path="alpha_index.rst",
            doc_type=DocType.ALPHA_INDEX,
            title="Function Index",
            sections=["index"],
            code_blocks=[],
            field_lists=[],
            raw_doc=None,
        )

        findings = checker.check(parsed, persona_name="newcomer")
        assert findings == []

        findings_all = checker.check(parsed, persona_name="all")
        assert findings_all == []

"""Tests for deep validation report formatters."""

import json

import pytest
from rich.console import Console

from gauss_doc_qa.deep.models import DeepCheckResult, DeepCheckType, DeepFunctionResult
from gauss_doc_qa.deep.report import (
    render_deep_json,
    render_deep_markdown,
    render_deep_terminal,
)


def _make_result(
    name: str,
    sig_pass: bool = True,
    ex_pass: bool = True,
    ret_pass: bool = True,
    sa_pass: bool = True,
) -> DeepFunctionResult:
    """Build a DeepFunctionResult with configurable check results."""
    checks = [
        DeepCheckResult(DeepCheckType.SIGNATURE_COMPLETE, sig_pass, "sig detail"),
        DeepCheckResult(DeepCheckType.EXAMPLES_NONTRIVIAL, ex_pass, "ex detail"),
        DeepCheckResult(DeepCheckType.RETURN_TYPE_DOCUMENTED, ret_pass, "ret detail"),
        DeepCheckResult(DeepCheckType.SEEALSO_PRESENT, sa_pass, "sa detail"),
    ]
    return DeepFunctionResult(
        function_name=name,
        doc_page=f"command_ref/{name}",
        file_path=f"/docs/{name}.rst",
        checks=checks,
        overall_pass=all(c.passed for c in checks),
    )


@pytest.fixture
def all_pass_results():
    return [_make_result("ols"), _make_result("meanc")]


@pytest.fixture
def mixed_results():
    return [
        _make_result("ols"),
        _make_result("badsig", sig_pass=False, sa_pass=False),
        _make_result("trivial", ex_pass=False),
    ]


class TestTerminalReport:
    """Terminal (Rich) output tests."""

    def test_contains_function_names(self, mixed_results):
        console = Console(file=None, force_terminal=True, width=120)
        with console.capture() as capture:
            render_deep_terminal(mixed_results, console=console)

        output = capture.get()
        assert "ols" in output
        assert "badsig" in output
        assert "trivial" in output

    def test_contains_pass_fail(self, mixed_results):
        console = Console(file=None, force_terminal=True, width=120)
        with console.capture() as capture:
            render_deep_terminal(mixed_results, console=console)

        output = capture.get()
        assert "PASS" in output
        assert "FAIL" in output

    def test_summary_line(self, mixed_results):
        console = Console(file=None, no_color=True, width=120)
        with console.capture() as capture:
            render_deep_terminal(mixed_results, console=console)

        output = capture.get()
        assert "1/3" in output

    def test_empty_results(self):
        console = Console(file=None, no_color=True, width=120)
        with console.capture() as capture:
            render_deep_terminal([], console=console)

        output = capture.get()
        assert "0/0" in output


class TestJsonReport:
    """JSON output tests."""

    def test_parses_as_valid_json(self, mixed_results):
        result = render_deep_json(mixed_results)
        data = json.loads(result)
        assert "summary" in data
        assert "functions" in data

    def test_summary_counts(self, mixed_results):
        data = json.loads(render_deep_json(mixed_results))
        assert data["summary"]["total"] == 3
        assert data["summary"]["passed"] == 1
        assert data["summary"]["failed"] == 2

    def test_all_passing_summary(self, all_pass_results):
        data = json.loads(render_deep_json(all_pass_results))
        assert data["summary"]["total"] == 2
        assert data["summary"]["passed"] == 2
        assert data["summary"]["failed"] == 0

    def test_function_data(self, mixed_results):
        data = json.loads(render_deep_json(mixed_results))
        names = [f["function_name"] for f in data["functions"]]
        assert "ols" in names
        assert "badsig" in names

    def test_empty_results(self):
        data = json.loads(render_deep_json([]))
        assert data["summary"]["total"] == 0
        assert data["functions"] == []


class TestMarkdownReport:
    """Markdown output tests."""

    def test_contains_header(self, mixed_results):
        md = render_deep_markdown(mixed_results)
        assert "# Deep Validation Report" in md

    def test_contains_table_headers(self, mixed_results):
        md = render_deep_markdown(mixed_results)
        assert "Function" in md
        assert "Signature" in md
        assert "Examples" in md
        assert "Return Type" in md
        assert "See Also" in md
        assert "Status" in md

    def test_contains_function_names(self, mixed_results):
        md = render_deep_markdown(mixed_results)
        assert "ols" in md
        assert "badsig" in md
        assert "trivial" in md

    def test_summary_count(self, mixed_results):
        md = render_deep_markdown(mixed_results)
        assert "1/3" in md

    def test_all_passing(self, all_pass_results):
        md = render_deep_markdown(all_pass_results)
        assert "2/2" in md
        # No "Failed Functions" section when all pass
        assert "## Failed Functions" not in md

    def test_failed_functions_section(self, mixed_results):
        md = render_deep_markdown(mixed_results)
        assert "## Failed Functions" in md
        assert "### badsig" in md
        assert "### trivial" in md

    def test_empty_results(self):
        md = render_deep_markdown([])
        assert "0/0" in md

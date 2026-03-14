import json
from io import StringIO

import pytest
from rich.console import Console

from gauss_doc_qa.models import Finding, Severity
from gauss_doc_qa.report.summary import build_summary
from gauss_doc_qa.report.json_report import render_json
from gauss_doc_qa.report.markdown_report import render_markdown
from gauss_doc_qa.report.terminal import render_terminal


SAMPLE_FINDINGS = [
    Finding(
        file="abs.rst",
        line=None,
        severity=Severity.WARNING,
        category="missing_code_block",
        checker="code_blocks",
        message="Command Reference page has no code blocks",
    ),
    Finding(
        file="olsmt.rst",
        line=42,
        severity=Severity.ERROR,
        category="empty_code_block",
        checker="code_blocks",
        message="Code block is empty or whitespace-only",
    ),
    Finding(
        file="anova.rst",
        line=None,
        severity=Severity.WARNING,
        category="missing_section",
        checker="sections",
        message="Missing required section: Examples",
    ),
    Finding(
        file="myproc.rst",
        line=None,
        severity=Severity.INFO,
        category="missing_return_type",
        checker="signatures",
        message="Function has :param: fields but no :return: documentation",
    ),
]


# -- Summary tests --

def test_summary_total():
    summary = build_summary(SAMPLE_FINDINGS)
    assert summary["total"] == 4


def test_summary_by_severity():
    summary = build_summary(SAMPLE_FINDINGS)
    assert summary["by_severity"]["error"] == 1
    assert summary["by_severity"]["warning"] == 2
    assert summary["by_severity"]["info"] == 1


def test_summary_by_category():
    summary = build_summary(SAMPLE_FINDINGS)
    assert summary["by_category"]["missing_code_block"] == 1
    assert summary["by_category"]["empty_code_block"] == 1
    assert summary["by_category"]["missing_section"] == 1
    assert summary["by_category"]["missing_return_type"] == 1


def test_summary_empty():
    summary = build_summary([])
    assert summary["total"] == 0
    assert summary["by_severity"] == {}
    assert summary["by_category"] == {}
    assert summary["by_severity_category"] == {}


# -- JSON tests --

def test_json_valid():
    result = render_json(SAMPLE_FINDINGS)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_json_has_summary():
    result = render_json(SAMPLE_FINDINGS)
    parsed = json.loads(result)
    assert "summary" in parsed
    assert parsed["summary"]["total"] == 4


def test_json_has_findings():
    result = render_json(SAMPLE_FINDINGS)
    parsed = json.loads(result)
    assert "findings" in parsed
    assert len(parsed["findings"]) == 4


def test_json_finding_severity_is_string():
    result = render_json(SAMPLE_FINDINGS)
    parsed = json.loads(result)
    for finding in parsed["findings"]:
        assert isinstance(finding["severity"], str)


# -- Markdown tests --

def test_markdown_has_header():
    result = render_markdown(SAMPLE_FINDINGS)
    assert "# GAUSS Doc QA Report" in result


def test_markdown_has_severity_table():
    result = render_markdown(SAMPLE_FINDINGS)
    assert "| ERROR | 1 |" in result


def test_markdown_has_findings_table():
    result = render_markdown(SAMPLE_FINDINGS)
    assert "| WARNING | abs.rst |" in result


# -- Terminal tests --

def test_terminal_no_crash():
    buf = StringIO()
    console = Console(file=buf, no_color=True)
    render_terminal(SAMPLE_FINDINGS, console)
    output = buf.getvalue()
    assert "ERROR: 1" in output
    assert "WARNING: 2" in output


def test_terminal_empty():
    buf = StringIO()
    console = Console(file=buf, no_color=True)
    render_terminal([], console)
    output = buf.getvalue()
    assert "No issues found" in output

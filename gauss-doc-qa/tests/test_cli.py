"""Integration tests for the CLI entry point."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from gauss_doc_qa.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def fixtures_path():
    return str(Path(__file__).parent / "fixtures")


def test_scan_terminal(runner, fixtures_path):
    result = runner.invoke(cli, ["--docs-dir", fixtures_path, "scan"])
    assert result.exit_code == 0, result.output
    assert "GAUSS Doc QA Report" in result.output


def test_scan_json(runner, fixtures_path):
    result = runner.invoke(cli, ["--docs-dir", fixtures_path, "scan", "--format", "json"])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert "summary" in parsed
    assert "findings" in parsed


def test_scan_markdown(runner, fixtures_path):
    result = runner.invoke(cli, ["--docs-dir", fixtures_path, "scan", "--format", "markdown"])
    assert result.exit_code == 0, result.output
    assert "# GAUSS Doc QA Report" in result.output


def test_scan_specific_checker(runner, fixtures_path):
    result = runner.invoke(cli, [
        "--docs-dir", fixtures_path, "scan",
        "--check", "code_blocks", "--format", "json",
    ])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    for finding in parsed["findings"]:
        assert finding["checker"] == "code_blocks"


def test_inventory(runner, fixtures_path):
    result = runner.invoke(cli, ["--docs-dir", fixtures_path, "inventory"])
    assert result.exit_code == 0, result.output
    assert "Total RST files:" in result.output


def test_scan_finds_issues(runner, fixtures_path):
    result = runner.invoke(cli, ["--docs-dir", fixtures_path, "scan", "--format", "json"])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["summary"]["total"] > 0, "Expected fixtures to produce findings"


def test_scan_output_to_file(runner, fixtures_path, tmp_path):
    output_file = str(tmp_path / "report.json")
    result = runner.invoke(cli, [
        "--docs-dir", fixtures_path, "scan",
        "--format", "json", "--output", output_file,
    ])
    assert result.exit_code == 0, result.output
    assert Path(output_file).exists()
    parsed = json.loads(Path(output_file).read_text())
    assert "summary" in parsed
    assert "findings" in parsed

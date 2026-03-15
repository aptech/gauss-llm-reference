"""Integration tests for the CLI entry point."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

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


# --- check-refs and --sphinx tests ---

def _make_mock_env():
    """Create a mock Sphinx BuildEnvironment for testing."""
    mock_env = MagicMock()
    mock_env.all_docs = {"test": 1234}
    mock_env.domaindata = {"gauss": {"objects": {}}}
    mock_env.toctree_includes = {}
    mock_env.metadata = {}
    mock_env.included = {}
    mock_env.config = MagicMock()
    mock_env.config.root_doc = "index"
    return mock_env


def test_check_refs_help(runner):
    """check-refs subcommand shows help."""
    result = runner.invoke(cli, ["--docs-dir", "/tmp", "check-refs", "--help"])
    assert result.exit_code == 0
    assert "cross-reference" in result.output.lower() or "check-refs" in result.output.lower()


def test_check_refs_invokes_sphinx_env(runner, tmp_path):
    """check-refs loads Sphinx env and runs sphinx checkers."""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\nSome content.\n")

    mock_env = _make_mock_env()

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "check-refs"])
        assert result.exit_code == 0, result.output
        assert "Loading Sphinx environment" in result.output


def test_check_refs_json_format(runner, tmp_path):
    """check-refs outputs valid JSON when --format json is used."""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\nSome content.\n")

    mock_env = _make_mock_env()

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "check-refs", "--format", "json",
        ])
        assert result.exit_code == 0, result.output
        # Output includes the echo lines before JSON; extract the JSON part
        lines = result.output.strip().split("\n")
        json_lines = [l for l in lines if not l.startswith("Loading") and not l.startswith("Sphinx")]
        json_text = "\n".join(json_lines)
        parsed = json.loads(json_text)
        assert "summary" in parsed
        assert "findings" in parsed


def test_check_refs_specific_checker(runner, tmp_path):
    """check-refs --check links runs only the links checker."""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\n:func:`abs`\n")

    mock_env = _make_mock_env()
    mock_env.domaindata = {"gauss": {"objects": {"abs": ("abs", "function")}}}

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "check-refs", "--check", "links",
        ])
        assert result.exit_code == 0, result.output


def test_scan_sphinx_flag_help(runner):
    """scan --sphinx flag appears in help."""
    result = runner.invoke(cli, ["--docs-dir", "/tmp", "scan", "--help"])
    assert result.exit_code == 0
    assert "--sphinx" in result.output


def test_scan_with_sphinx_flag(runner, tmp_path):
    """scan --sphinx runs both fast and sphinx-mode checkers."""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\nSome content.\n")

    mock_env = _make_mock_env()

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "scan", "--sphinx",
        ])
        assert result.exit_code == 0, result.output
        assert "Loading Sphinx environment" in result.output


def test_sphinx_checkers_registered():
    """All four sphinx checkers are registered."""
    from gauss_doc_qa.checkers import get_all_sphinx_checkers
    names = {c.name for c in get_all_sphinx_checkers()}
    assert "links" in names
    assert "orphans" in names
    assert "coverage" in names
    assert "seealso" in names

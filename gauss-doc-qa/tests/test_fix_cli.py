"""Integration tests for the fix CLI subcommand."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from gauss_doc_qa.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def _make_mock_env(gauss_objects=None):
    """Create a mock Sphinx BuildEnvironment with gauss objects."""
    mock_env = MagicMock()
    mock_env.all_docs = {"test": 1234}
    if gauss_objects is None:
        gauss_objects = {}
    mock_env.domaindata = {
        "gauss": {"objects": gauss_objects},
        "std": {"labels": {}},
    }
    mock_env.toctree_includes = {}
    mock_env.metadata = {}
    mock_env.included = {}
    mock_env.config = MagicMock()
    mock_env.config.root_doc = "index"
    return mock_env


def _ensure_sphinx_env_importable():
    """Ensure gauss_doc_qa.parser.sphinx_env can be imported even without sphinx.

    Injects a stub module into sys.modules if sphinx is not installed,
    so that unittest.mock.patch can resolve the target path.
    """
    if "gauss_doc_qa.parser.sphinx_env" not in sys.modules:
        stub = MagicMock()
        sys.modules["gauss_doc_qa.parser.sphinx_env"] = stub


@pytest.fixture(autouse=True)
def _setup_sphinx_stub():
    """Auto-use fixture: ensure sphinx_env is importable for patching."""
    _ensure_sphinx_env_importable()


def test_fix_dry_run_shows_diff(runner, tmp_path):
    """Default fix (no --apply) shows diff preview without modifying files.

    Uses 'plotBr' as the broken ref -- close enough to fuzzy-match 'plotBar'
    but not a casefold match, so LinksChecker flags it as broken.
    """
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nThe :func:`plotBr` function works.\n"
    rst_file.write_text(rst_content)

    gauss_objects = {
        "plotBar": ("plotBar", "function"),
        "ols": ("ols", "function"),
    }
    mock_env = _make_mock_env(gauss_objects)

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "fix"])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "plotBr" in result.output
    assert "plotBar" in result.output
    assert "Run with --apply" in result.output

    # File should NOT be modified
    assert rst_file.read_text() == rst_content


def test_fix_apply_writes_file(runner, tmp_path):
    """fix --apply modifies the RST file with corrections."""
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nThe :func:`plotBr` function works.\n"
    rst_file.write_text(rst_content)

    gauss_objects = {
        "plotBar": ("plotBar", "function"),
        "ols": ("ols", "function"),
    }
    mock_env = _make_mock_env(gauss_objects)

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "fix", "--apply"])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "Applied" in result.output
    assert "Run with --apply" not in result.output

    # File SHOULD be modified
    updated = rst_file.read_text()
    assert ":func:`plotBar`" in updated
    assert ":func:`plotBr`" not in updated


def test_fix_no_fixable_issues(runner, tmp_path):
    """fix with no broken refs shows 'No auto-fixable issues found.'"""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\nSome content with no references.\n")

    gauss_objects = {"plotBar": ("plotBar", "function")}
    mock_env = _make_mock_env(gauss_objects)

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "fix"])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "No auto-fixable issues found." in result.output


def test_fix_verify_after_apply(runner, tmp_path):
    """fix --apply --verify runs Sphinx build verification."""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\nThe :func:`plotBr` function works.\n")

    gauss_objects = {"plotBar": ("plotBar", "function")}
    mock_env = _make_mock_env(gauss_objects)

    verify_result = {"success": True, "warning_count": 0, "warnings": []}

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env), \
         patch("gauss_doc_qa.fixer.verify_sphinx_build", return_value=verify_result) as mock_verify:
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--apply", "--verify",
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    mock_verify.assert_called_once_with(str(Path(tmp_path).resolve()))
    assert "verification" in result.output.lower() or "Verification" in result.output


def test_fix_verify_without_apply_skips(runner, tmp_path):
    """fix --verify without --apply skips verification gracefully."""
    rst_file = tmp_path / "test.rst"
    rst_file.write_text("Title\n=====\n\nThe :func:`plotBr` function works.\n")

    gauss_objects = {"plotBar": ("plotBar", "function")}
    mock_env = _make_mock_env(gauss_objects)

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--verify",
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "Skipping --verify" in result.output


def test_fix_min_confidence_filter(runner, tmp_path):
    """fix --min-confidence 0.99 filters out lower-confidence matches."""
    rst_file = tmp_path / "test.rst"
    # "plotBr" vs "plotBar" fuzzy-matches but below 0.99
    rst_file.write_text("Title\n=====\n\nThe :func:`plotBr` function works.\n")

    gauss_objects = {"plotBar": ("plotBar", "function")}
    mock_env = _make_mock_env(gauss_objects)

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--min-confidence", "0.99",
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "No auto-fixable issues found." in result.output

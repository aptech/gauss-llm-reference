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


def _make_mock_env(gauss_objects=None, all_docs=None, std_labels=None):
    """Create a mock Sphinx BuildEnvironment with gauss objects."""
    mock_env = MagicMock()
    mock_env.all_docs = all_docs if all_docs is not None else {"test": 1234}
    if gauss_objects is None:
        gauss_objects = {}
    if std_labels is None:
        std_labels = {}
    mock_env.domaindata = {
        "gauss": {"objects": gauss_objects},
        "std": {"labels": std_labels},
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


# --- Extended fix tests: :doc:, :ref:, and glossary ---


def test_fix_dry_run_doc_ref(runner, tmp_path):
    """fix resolves broken :doc: references via fuzzy matching (dry-run)."""
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nSee :doc:`command-reference/plotBr` for details.\n"
    rst_file.write_text(rst_content)

    # The doc "command-reference/plotBar" exists but "command-reference/plotBr" does not
    mock_env = _make_mock_env(
        all_docs={"command-reference/plotBar": 1234, "index": 1234},
    )

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "fix"])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "plotBr" in result.output
    assert "plotBar" in result.output
    assert "Run with --apply" in result.output

    # File should NOT be modified (dry-run)
    assert rst_file.read_text() == rst_content


def test_fix_dry_run_ref(runner, tmp_path):
    """fix resolves broken :ref: references via fuzzy matching (dry-run)."""
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nSee :ref:`getting-startd` for setup.\n"
    rst_file.write_text(rst_content)

    # Label "getting-started" exists but "getting-startd" does not
    mock_env = _make_mock_env(
        std_labels={"getting-started": ("doc", "label", "Getting Started")},
    )

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "fix"])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "getting-startd" in result.output
    assert "getting-started" in result.output
    assert "Run with --apply" in result.output

    # File should NOT be modified (dry-run)
    assert rst_file.read_text() == rst_content


def test_fix_apply_doc_ref(runner, tmp_path):
    """fix --apply writes corrected :doc: references to disk."""
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nSee :doc:`command-reference/plotBr` for details.\n"
    rst_file.write_text(rst_content)

    mock_env = _make_mock_env(
        all_docs={"command-reference/plotBar": 1234, "index": 1234},
    )

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, ["--docs-dir", str(tmp_path), "fix", "--apply"])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "Applied" in result.output

    # File SHOULD be modified
    updated = rst_file.read_text()
    assert ":doc:`command-reference/plotBar`" in updated
    assert "plotBr" not in updated


def _write_glossary_yaml(tmp_path):
    """Helper: write a glossary YAML file and return its path."""
    glossary_file = tmp_path / "glossary.yml"
    glossary_file.write_text(
        "glossary:\n"
        "  - canonical: \"GAUSS\"\n"
        "    aliases: [\"Gauss\"]\n"
        "    category: \"product\"\n"
        "    description: \"Always uppercase when referring to the software\"\n"
    )
    return str(glossary_file)


def test_fix_glossary_dry_run(runner, tmp_path):
    """fix --glossary shows terminology fix proposals without modifying files."""
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nGauss is a programming language.\n"
    rst_file.write_text(rst_content)

    glossary_path = _write_glossary_yaml(tmp_path)
    mock_env = _make_mock_env()

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--glossary", glossary_path,
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "Gauss" in result.output
    assert "GAUSS" in result.output
    assert "Run with --apply" in result.output

    # File should NOT be modified (dry-run)
    assert rst_file.read_text() == rst_content


def test_fix_glossary_apply(runner, tmp_path):
    """fix --glossary --apply writes terminology corrections to disk."""
    rst_file = tmp_path / "test.rst"
    rst_content = "Title\n=====\n\nGauss is a programming language.\n"
    rst_file.write_text(rst_content)

    glossary_path = _write_glossary_yaml(tmp_path)
    mock_env = _make_mock_env()

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--glossary", glossary_path, "--apply",
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    assert "Applied" in result.output

    # File SHOULD be modified
    updated = rst_file.read_text()
    assert "GAUSS is a programming language." in updated
    assert "Gauss is" not in updated


def test_fix_glossary_skips_code_blocks(runner, tmp_path):
    """fix --glossary --apply does NOT modify terms inside code blocks."""
    rst_file = tmp_path / "test.rst"
    # "Gauss" appears in prose AND inside a code block
    rst_content = (
        "Title\n"
        "=====\n"
        "\n"
        "Gauss is great.\n"
        "\n"
        "Example::\n"
        "\n"
        "    Gauss code here\n"
        "\n"
        "More text.\n"
    )
    rst_file.write_text(rst_content)

    glossary_path = _write_glossary_yaml(tmp_path)
    mock_env = _make_mock_env()

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--glossary", glossary_path, "--apply",
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"

    updated = rst_file.read_text()
    # Prose line should be fixed
    assert "GAUSS is great." in updated
    # Code block line should be untouched
    assert "    Gauss code here" in updated


def test_fix_combined_ref_and_glossary(runner, tmp_path):
    """fix --glossary combines ref fixes and glossary fixes in one run."""
    rst_file = tmp_path / "test.rst"
    rst_content = (
        "Title\n"
        "=====\n"
        "\n"
        "The :func:`plotBr` function.\n"
        "\n"
        "Gauss is great.\n"
    )
    rst_file.write_text(rst_content)

    glossary_path = _write_glossary_yaml(tmp_path)
    gauss_objects = {"plotBar": ("plotBar", "function")}
    mock_env = _make_mock_env(gauss_objects=gauss_objects)

    with patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env", return_value=mock_env):
        result = runner.invoke(cli, [
            "--docs-dir", str(tmp_path), "fix", "--glossary", glossary_path,
        ])

    assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
    # Both fix types should appear in output
    assert "plotBr" in result.output
    assert "plotBar" in result.output
    assert "Gauss" in result.output
    assert "GAUSS" in result.output
    assert "Run with --apply" in result.output

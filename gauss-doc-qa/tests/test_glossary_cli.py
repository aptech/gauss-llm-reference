"""CLI integration tests for glossary scanning and report output."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from gauss_doc_qa.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def glossary_yaml(tmp_path):
    """Write a YAML glossary file with known entries."""
    content = """\
glossary:
  - canonical: "GAUSS"
    aliases: ["Gauss", "gauss"]
    category: "product"
  - canonical: "dataframe"
    aliases: ["data frame", "DataFrame"]
    category: "concept"
"""
    path = tmp_path / "glossary.yaml"
    path.write_text(content)
    return str(path)


@pytest.fixture
def docs_with_aliases(tmp_path):
    """Create a docs directory with RST files containing non-canonical terms."""
    docs = tmp_path / "docs_alias"
    docs.mkdir()
    # Minimal conf.py for scan to find
    (docs / "conf.py").write_text("exclude_patterns = []\n")
    rst = docs / "test_page.rst"
    rst.write_text(
        "Test Page\n"
        "=========\n"
        "\n"
        "This page discusses Gauss programming.\n"
        "We use data frame operations here.\n"
    )
    return str(docs)


@pytest.fixture
def docs_canonical_only(tmp_path):
    """Create docs with only canonical terms -- should produce zero glossary findings."""
    docs = tmp_path / "docs_canon"
    docs.mkdir()
    (docs / "conf.py").write_text("exclude_patterns = []\n")
    rst = docs / "test_page.rst"
    rst.write_text(
        "Test Page\n"
        "=========\n"
        "\n"
        "This page discusses GAUSS programming.\n"
        "We use dataframe operations here.\n"
    )
    return str(docs)


class TestGlossaryScanFindings:
    """Tests that glossary scanning detects non-canonical terms."""

    def test_scan_with_glossary_finds_aliases(
        self, runner, glossary_yaml, docs_with_aliases
    ):
        # Use JSON format for reliable assertion (terminal Rich table truncates)
        result = runner.invoke(
            cli,
            [
                "--docs-dir",
                docs_with_aliases,
                "scan",
                "--glossary",
                glossary_yaml,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        glossary_findings = [
            f for f in parsed["findings"] if f.get("checker") == "glossary"
        ]
        assert len(glossary_findings) >= 2, (
            f"Expected at least 2 glossary findings, got {len(glossary_findings)}"
        )
        messages = " ".join(f["message"] for f in glossary_findings)
        assert "Non-canonical term" in messages
        assert "Gauss" in messages
        assert "GAUSS" in messages

    def test_scan_with_glossary_no_findings_on_canonical(
        self, runner, glossary_yaml, docs_canonical_only
    ):
        result = runner.invoke(
            cli,
            [
                "--docs-dir",
                docs_canonical_only,
                "scan",
                "--glossary",
                glossary_yaml,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        terminology_findings = [
            f for f in parsed["findings"] if f.get("category") == "terminology"
        ]
        assert len(terminology_findings) == 0, (
            f"Expected zero terminology findings on canonical text, got {len(terminology_findings)}"
        )

    def test_scan_without_glossary_no_terminology_findings(
        self, runner, docs_with_aliases
    ):
        result = runner.invoke(
            cli,
            ["--docs-dir", docs_with_aliases, "scan", "--format", "json"],
        )
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        terminology_findings = [
            f for f in parsed["findings"] if f.get("category") == "terminology"
        ]
        assert len(terminology_findings) == 0, (
            "Glossary checker should not run without --glossary flag"
        )


class TestGlossaryOutputFormats:
    """Tests that glossary findings flow through all three report formats."""

    def test_scan_glossary_json_format(
        self, runner, glossary_yaml, docs_with_aliases
    ):
        result = runner.invoke(
            cli,
            [
                "--docs-dir",
                docs_with_aliases,
                "scan",
                "--glossary",
                glossary_yaml,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        glossary_findings = [
            f for f in parsed["findings"] if f.get("checker") == "glossary"
        ]
        assert len(glossary_findings) >= 1, "Expected at least one glossary finding in JSON"
        for f in glossary_findings:
            assert f["category"] == "terminology"
            assert f["checker"] == "glossary"

    def test_scan_glossary_markdown_format(
        self, runner, glossary_yaml, docs_with_aliases
    ):
        result = runner.invoke(
            cli,
            [
                "--docs-dir",
                docs_with_aliases,
                "scan",
                "--glossary",
                glossary_yaml,
                "--format",
                "markdown",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "glossary" in result.output.lower()
        assert "terminology" in result.output.lower()


class TestGlossaryEdgeCases:
    """Tests for error handling and edge cases."""

    def test_scan_glossary_invalid_path(self, runner, docs_with_aliases):
        result = runner.invoke(
            cli,
            [
                "--docs-dir",
                docs_with_aliases,
                "scan",
                "--glossary",
                "/nonexistent/glossary.yaml",
            ],
        )
        # click.Path(exists=True) should reject nonexistent path
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower() or "error" in result.output.lower() or "invalid" in result.output.lower()

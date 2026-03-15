"""Tests for the glossary fixer module."""

from __future__ import annotations

from pathlib import Path

import pytest

from gauss_doc_qa.fixer.glossary_fixer import resolve_glossary_fixes
from gauss_doc_qa.glossary import GlossaryEntry
from gauss_doc_qa.models import Finding, Severity


# Shared glossary entries for testing
GLOSSARY_ENTRIES = [
    GlossaryEntry(
        canonical="GAUSS",
        aliases=["Gauss", "gauss"],
        category="product",
        description="Always uppercase when referring to the software",
    ),
    GlossaryEntry(
        canonical="DataFrame",
        aliases=["dataframe", "data frame"],
        category="concept",
    ),
]


class TestResolveGlossaryFixes:
    """Tests for resolve_glossary_fixes()."""

    def test_resolve_glossary_basic(self, tmp_path: Path):
        """Basic alias-to-canonical replacement should work."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("Gauss is great software.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="terminology",
                checker="glossary",
                message="Non-canonical term 'Gauss' found. Use 'GAUSS' instead.",
            )
        ]

        proposals = resolve_glossary_fixes(findings, GLOSSARY_ENTRIES)

        assert len(proposals) == 1
        p = proposals[0]
        assert p.fixed_text == "GAUSS is great software."
        assert p.old_target == "Gauss"
        assert p.new_target == "GAUSS"
        assert p.confidence == 1.0
        assert p.category == "terminology"

    def test_resolve_glossary_multiple_occurrences(self, tmp_path: Path):
        """All occurrences of the alias on the line should be replaced."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("Gauss and Gauss are both wrong.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="terminology",
                checker="glossary",
                message="Non-canonical term 'Gauss' found. Use 'GAUSS' instead.",
            )
        ]

        proposals = resolve_glossary_fixes(findings, GLOSSARY_ENTRIES)

        assert len(proposals) == 1
        assert proposals[0].fixed_text == "GAUSS and GAUSS are both wrong."

    def test_resolve_glossary_skips_non_terminology(self, tmp_path: Path):
        """Findings with non-terminology category should be ignored."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("See :func:`plotbar` for details.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.ERROR,
                category="broken_func_ref",
                checker="links",
                message="Broken :func: reference to 'plotbar'",
            )
        ]

        proposals = resolve_glossary_fixes(findings, GLOSSARY_ENTRIES)
        assert len(proposals) == 0

    def test_resolve_glossary_preserves_canonical(self, tmp_path: Path):
        """No FixProposal if the word is already the canonical form."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("GAUSS is great software.\n")

        # Edge case: checker shouldn't produce this finding, but guard anyway
        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="terminology",
                checker="glossary",
                message="Non-canonical term 'GAUSS' found. Use 'GAUSS' instead.",
            )
        ]

        proposals = resolve_glossary_fixes(findings, GLOSSARY_ENTRIES)
        # re.sub replaces GAUSS with GAUSS -> identical line -> skipped
        assert len(proposals) == 0

    def test_resolve_glossary_word_boundary(self, tmp_path: Path):
        """Word boundary regex should prevent partial-word replacement."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("GAUSSX should not be affected.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="terminology",
                checker="glossary",
                message="Non-canonical term 'Gauss' found. Use 'GAUSS' instead.",
            )
        ]

        proposals = resolve_glossary_fixes(findings, GLOSSARY_ENTRIES)
        # "Gauss" is not present on the line (only "GAUSSX"), so no replacement
        assert len(proposals) == 0

    def test_resolve_glossary_multiword_alias(self, tmp_path: Path):
        """Multi-word aliases like 'data frame' should be replaced."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("Create a data frame from a matrix.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="terminology",
                checker="glossary",
                message="Non-canonical term 'data frame' found. Use 'DataFrame' instead.",
            )
        ]

        proposals = resolve_glossary_fixes(findings, GLOSSARY_ENTRIES)

        assert len(proposals) == 1
        assert proposals[0].fixed_text == "Create a DataFrame from a matrix."
        assert proposals[0].old_target == "data frame"
        assert proposals[0].new_target == "DataFrame"

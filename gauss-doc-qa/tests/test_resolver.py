"""Tests for the fixer resolver module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from gauss_doc_qa.fixer.resolver import (
    resolve_func_ref,
    resolve_doc_ref,
    resolve_ref_ref,
    resolve_fixes,
)
from gauss_doc_qa.models import Finding, Severity

# A realistic set of known GAUSS function names for testing
KNOWN_NAMES = [
    "plotBar",
    "plotBox",
    "plotXY",
    "plotScatter",
    "plotHist",
    "olsmt",
    "stdc",
    "meanc",
    "sumc",
]


class TestResolveFuncRef:
    """Tests for resolve_func_ref()."""

    def test_resolve_func_ref_exact_case_mismatch(self):
        """'plotbar' should match 'plotBar' (case mismatch)."""
        result = resolve_func_ref("plotbar", KNOWN_NAMES)
        assert result is not None
        name, confidence = result
        assert name == "plotBar"
        assert confidence >= 0.85

    def test_resolve_func_ref_typo(self):
        """'plotBr' should match 'plotBar' with a single close match."""
        # 'plotBr' is close to 'plotBar' (5/7 chars)
        result = resolve_func_ref("plotBr", KNOWN_NAMES, min_confidence=0.7)
        assert result is not None
        name, confidence = result
        assert name == "plotBar"

    def test_resolve_func_ref_no_match(self):
        """'xyznonexistent' should return None (no close match)."""
        result = resolve_func_ref("xyznonexistent", KNOWN_NAMES)
        assert result is None

    def test_resolve_func_ref_ambiguous(self):
        """Target matching multiple names within 0.05 should return None."""
        # 'plotBo' is close to both 'plotBar' and 'plotBox' (same edit distance)
        # Use names that will produce nearly identical scores
        ambiguous_names = ["plotBar", "plotBax", "plotBaz"]
        result = resolve_func_ref("plotBa", ambiguous_names, min_confidence=0.5)
        assert result is None

    def test_resolve_func_ref_clear_winner(self):
        """Top match >0.05 better than second should return the top match."""
        # 'plotBars' is very close to 'plotBar' but not to 'plotBox'
        result = resolve_func_ref("plotBars", KNOWN_NAMES, min_confidence=0.7)
        assert result is not None
        name, _ = result
        assert name == "plotBar"

    def test_resolve_func_ref_empty_known_names(self):
        """Empty known_names list should return None."""
        result = resolve_func_ref("plotbar", [])
        assert result is None


class TestResolveFixes:
    """Tests for resolve_fixes()."""

    def test_resolve_fixes_from_findings(self, tmp_path: Path):
        """Broken func ref findings should produce FixProposals."""
        # Create a test RST file
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "Line 1\n"
            "See :func:`plotbar` for details.\n"
            "Line 3\n"
        )

        findings = [
            Finding(
                file=str(rst_file),
                line=2,
                severity=Severity.ERROR,
                category="broken_func_ref",
                checker="links",
                message="Broken :func: reference to 'plotbar'",
            )
        ]

        gauss_objects = {name: {} for name in KNOWN_NAMES}
        proposals = resolve_fixes(findings, gauss_objects)

        assert len(proposals) == 1
        p = proposals[0]
        assert p.old_target == "plotbar"
        assert p.new_target == "plotBar"
        assert p.file_path == str(rst_file)
        assert p.line_number == 2
        assert "plotBar" in p.fixed_text
        assert "plotbar" not in p.fixed_text
        assert p.category == "broken_func_ref"
        assert p.confidence >= 0.85
        assert p.finding is findings[0]

    def test_resolve_fixes_skips_non_func_findings(self, tmp_path: Path):
        """Findings with non-func categories should be ignored."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("See :ref:`some_label` for details.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="broken_ref",
                checker="links",
                message="Broken :ref: reference to 'some_label'",
            )
        ]

        gauss_objects = {name: {} for name in KNOWN_NAMES}
        proposals = resolve_fixes(findings, gauss_objects)

        assert len(proposals) == 0


# Known document paths for testing
KNOWN_DOCS = [
    "command-reference/plotBar",
    "command-reference/plotBox",
    "command-reference/plotXY",
    "user-guide/getting-started",
    "user-guide/installation",
]

# Known ref labels for testing
KNOWN_LABELS = [
    "getting-started",
    "installation-guide",
    "data-loading",
    "matrix-operations",
]


class TestDocRefResolver:
    """Tests for resolve_doc_ref()."""

    def test_exact_doc_match(self):
        """Exact match should be returned."""
        result = resolve_doc_ref("command-reference/plotBar", KNOWN_DOCS)
        assert result is not None
        name, confidence = result
        assert name == "command-reference/plotBar"
        assert confidence >= 0.85

    def test_close_doc_match(self):
        """'command-reference/plotBars' should resolve to 'command-reference/plotBar'."""
        # 'plotBars' is close to 'plotBar' but far from 'plotBox'/'plotXY'
        result = resolve_doc_ref("command-reference/plotBars", KNOWN_DOCS, min_confidence=0.7)
        assert result is not None
        name, confidence = result
        assert name == "command-reference/plotBar"

    def test_no_doc_match(self):
        """'totally-nonexistent-page' should return None."""
        result = resolve_doc_ref("totally-nonexistent-page", KNOWN_DOCS)
        assert result is None

    def test_ambiguous_doc_match(self):
        """Two equally close doc names should return None."""
        ambiguous_docs = ["command-reference/plotBar", "command-reference/plotBax"]
        result = resolve_doc_ref("command-reference/plotBa", ambiguous_docs, min_confidence=0.5)
        assert result is None


class TestRefRefResolver:
    """Tests for resolve_ref_ref()."""

    def test_exact_label_match(self):
        """Exact label should be matched."""
        result = resolve_ref_ref("getting-started", KNOWN_LABELS)
        assert result is not None
        name, confidence = result
        assert name == "getting-started"
        assert confidence >= 0.80

    def test_close_label_match(self):
        """'getting-startd' should resolve to 'getting-started'."""
        result = resolve_ref_ref("getting-startd", KNOWN_LABELS, min_confidence=0.7)
        assert result is not None
        name, confidence = result
        assert name == "getting-started"

    def test_no_label_match(self):
        """'zzz-nonexistent' should return None."""
        result = resolve_ref_ref("zzz-nonexistent", KNOWN_LABELS)
        assert result is None


class TestResolvFixesExtended:
    """Tests for resolve_fixes() with doc/ref support."""

    def test_resolve_broken_doc_ref(self, tmp_path: Path):
        """broken_doc_ref Finding should produce FixProposal with :doc: pattern."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "Line 1\n"
            "See :doc:`command-reference/plotBars` for details.\n"
            "Line 3\n"
        )

        findings = [
            Finding(
                file=str(rst_file),
                line=2,
                severity=Severity.ERROR,
                category="broken_doc_ref",
                checker="links",
                message="Broken :doc: reference to 'command-reference/plotBars'",
            )
        ]

        gauss_objects = {}
        proposals = resolve_fixes(
            findings, gauss_objects,
            min_confidence=0.7,
            doc_names=KNOWN_DOCS,
        )

        assert len(proposals) == 1
        p = proposals[0]
        assert p.old_target == "command-reference/plotBars"
        assert p.new_target == "command-reference/plotBar"
        assert p.category == "broken_doc_ref"
        assert ":doc:`command-reference/plotBar`" in p.fixed_text
        assert "command-reference/plotBars" not in p.fixed_text

    def test_resolve_broken_ref(self, tmp_path: Path):
        """broken_ref Finding should produce FixProposal with :ref: pattern."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "See :ref:`getting-startd` for details.\n"
        )

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.WARNING,
                category="broken_ref",
                checker="links",
                message="Broken :ref: reference to 'getting-startd'",
            )
        ]

        gauss_objects = {}
        proposals = resolve_fixes(
            findings, gauss_objects,
            min_confidence=0.7,
            label_names=KNOWN_LABELS,
        )

        assert len(proposals) == 1
        p = proposals[0]
        assert p.old_target == "getting-startd"
        assert p.new_target == "getting-started"
        assert p.category == "broken_ref"
        assert ":ref:`getting-started`" in p.fixed_text

    def test_func_refs_still_work(self, tmp_path: Path):
        """Existing broken_func_ref findings should still resolve correctly."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "See :func:`plotbar` for details.\n"
        )

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

        gauss_objects = {name: {} for name in KNOWN_NAMES}
        proposals = resolve_fixes(
            findings, gauss_objects,
            doc_names=KNOWN_DOCS,
            label_names=KNOWN_LABELS,
        )

        assert len(proposals) == 1
        p = proposals[0]
        assert p.old_target == "plotbar"
        assert p.new_target == "plotBar"
        assert p.category == "broken_func_ref"
        assert ":func:`plotBar`" in p.fixed_text
    def test_resolve_fixes_seealso_category(self, tmp_path: Path):
        """broken_seealso_ref findings should also produce FixProposals."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            ".. seealso::\n"
            "\n"
            "   :func:`plotbar` for bar charts\n"
        )

        findings = [
            Finding(
                file=str(rst_file),
                line=3,
                severity=Severity.ERROR,
                category="broken_seealso_ref",
                checker="seealso",
                message="Broken :func: reference to 'plotbar' in seealso directive",
            )
        ]

        gauss_objects = {name: {} for name in KNOWN_NAMES}
        proposals = resolve_fixes(findings, gauss_objects)

        assert len(proposals) == 1
        assert proposals[0].new_target == "plotBar"
        assert proposals[0].category == "broken_seealso_ref"

    def test_resolve_fixes_no_match_skipped(self, tmp_path: Path):
        """Findings with no close match should be skipped."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text("See :func:`xyznonexistent` for details.\n")

        findings = [
            Finding(
                file=str(rst_file),
                line=1,
                severity=Severity.ERROR,
                category="broken_func_ref",
                checker="links",
                message="Broken :func: reference to 'xyznonexistent'",
            )
        ]

        gauss_objects = {name: {} for name in KNOWN_NAMES}
        proposals = resolve_fixes(findings, gauss_objects)

        assert len(proposals) == 0

"""Tests for the fixer applier module."""

from __future__ import annotations

from pathlib import Path

import pytest

from gauss_doc_qa.fixer.applier import (
    compute_code_block_ranges,
    is_safe_to_fix,
    apply_fixes,
)
from gauss_doc_qa.fixer.models import FixProposal
from gauss_doc_qa.models import Finding, Severity


def _make_proposal(
    file_path: str,
    line_number: int,
    original_text: str = "See :func:`plotbar` here.",
    fixed_text: str = "See :func:`plotBar` here.",
    old_target: str = "plotbar",
    new_target: str = "plotBar",
) -> FixProposal:
    """Helper to create a FixProposal for testing."""
    return FixProposal(
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        fixed_text=fixed_text,
        old_target=old_target,
        new_target=new_target,
        category="broken_func_ref",
        confidence=0.95,
        finding=Finding(
            file=file_path,
            line=line_number,
            severity=Severity.ERROR,
            category="broken_func_ref",
            checker="links",
            message=f"Broken :func: reference to '{old_target}'",
        ),
    )


class TestIsSafeToFix:
    """Tests for is_safe_to_fix()."""

    def test_is_safe_paragraph_text(self):
        """Plain paragraph text with :func: should be safe."""
        line = "The :func:`plotbar` function draws a bar chart."
        assert is_safe_to_fix(line, 5, [line], []) is True

    def test_is_safe_seealso(self):
        """Line in seealso body should be safe."""
        lines = [
            ".. seealso::",
            "",
            "   :func:`plotbar` for bar charts",
        ]
        # The seealso directive line itself matches DIRECTIVE_RE but has "seealso"
        assert is_safe_to_fix(lines[0], 1, lines, []) is True
        # The content line is just indented text
        assert is_safe_to_fix(lines[2], 3, lines, []) is True

    def test_is_unsafe_table_grid(self):
        """Grid table border line should be unsafe."""
        line = "+------------+------------------+"
        assert is_safe_to_fix(line, 1, [line], []) is False

    def test_is_unsafe_table_cell(self):
        """Table cell line starting with | should be unsafe."""
        line = "| :func:`plotbar` | Bar chart   |"
        assert is_safe_to_fix(line, 1, [line], []) is False

    def test_is_unsafe_code_block(self):
        """Line inside a code block range should be unsafe."""
        line = "   :func:`plotbar`"
        code_ranges = [(3, 6)]
        assert is_safe_to_fix(line, 4, [line], code_ranges) is False

    def test_is_unsafe_directive(self):
        """Non-seealso directive line should be unsafe."""
        line = ".. function:: plotbar"
        assert is_safe_to_fix(line, 1, [line], []) is False

    def test_is_safe_outside_code_block(self):
        """Line outside code block range should be safe."""
        line = "See :func:`plotbar` for details."
        code_ranges = [(10, 15)]
        assert is_safe_to_fix(line, 5, [line], code_ranges) is True


class TestComputeCodeBlockRanges:
    """Tests for compute_code_block_ranges()."""

    def test_compute_code_block_ranges(self):
        """Should detect literal blocks with :: ending."""
        lines = [
            "Example usage::",        # line 1
            "",                        # line 2
            "   x = plotbar(data);",   # line 3 (code block)
            "   y = 42;",             # line 4 (code block)
            "",                        # line 5
            "Back to text.",          # line 6
        ]
        ranges = compute_code_block_ranges(lines)
        assert len(ranges) == 1
        start, end = ranges[0]
        assert start == 3
        assert end == 4

    def test_compute_code_block_directive(self):
        """Should detect .. code-block:: directives."""
        lines = [
            ".. code-block:: gauss",   # line 1
            "",                         # line 2
            "   x = 42;",              # line 3 (code block)
            "   y = 99;",              # line 4 (code block)
            "",                         # line 5
            "Normal text.",             # line 6
        ]
        ranges = compute_code_block_ranges(lines)
        assert len(ranges) == 1
        start, end = ranges[0]
        assert start == 3
        assert end == 4

    def test_compute_multiple_code_blocks(self):
        """Should detect multiple code blocks."""
        lines = [
            "First block::",           # line 1
            "",                         # line 2
            "   code1",                # line 3
            "",                         # line 4
            "Text between.",           # line 5
            "",                         # line 6
            "Second block::",          # line 7
            "",                         # line 8
            "   code2",                # line 9
            "",                         # line 10
        ]
        ranges = compute_code_block_ranges(lines)
        assert len(ranges) == 2


class TestApplyFixes:
    """Tests for apply_fixes()."""

    def test_apply_fixes_dry_run(self, tmp_path: Path):
        """In dry_run mode, proposals should be returned but file unchanged."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "Line 1\n"
            "See :func:`plotbar` for details.\n"
            "Line 3\n"
        )
        original_content = rst_file.read_text()

        proposal = _make_proposal(
            file_path=str(rst_file),
            line_number=2,
        )

        result = apply_fixes([proposal], dry_run=True)
        assert len(result) == 1
        # File should NOT be modified
        assert rst_file.read_text() == original_content

    def test_apply_fixes_apply(self, tmp_path: Path):
        """In apply mode, file content should be updated."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "Line 1\n"
            "See :func:`plotbar` for details.\n"
            "Line 3\n"
        )

        proposal = _make_proposal(
            file_path=str(rst_file),
            line_number=2,
        )

        result = apply_fixes([proposal], dry_run=False)
        assert len(result) == 1

        updated = rst_file.read_text()
        assert "plotBar" in updated
        assert "plotbar" not in updated

    def test_apply_fixes_skips_unsafe(self, tmp_path: Path):
        """Proposals on table lines should be skipped."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "Line 1\n"
            "| :func:`plotbar` | Bar chart   |\n"
            "Line 3\n"
        )
        original_content = rst_file.read_text()

        proposal = _make_proposal(
            file_path=str(rst_file),
            line_number=2,
            original_text="| :func:`plotbar` | Bar chart   |",
            fixed_text="| :func:`plotBar` | Bar chart   |",
        )

        result = apply_fixes([proposal], dry_run=False)
        assert len(result) == 0
        # File should NOT be modified
        assert rst_file.read_text() == original_content

    def test_apply_fixes_multiple_same_file(self, tmp_path: Path):
        """Multiple proposals in the same file should work bottom-up."""
        rst_file = tmp_path / "test.rst"
        rst_file.write_text(
            "See :func:`plotbar` here.\n"
            "Middle line.\n"
            "Also :func:`plotbar` there.\n"
        )

        p1 = _make_proposal(file_path=str(rst_file), line_number=1)
        p3 = _make_proposal(
            file_path=str(rst_file),
            line_number=3,
            original_text="Also :func:`plotbar` there.",
            fixed_text="Also :func:`plotBar` there.",
        )

        result = apply_fixes([p1, p3], dry_run=False)
        assert len(result) == 2

        updated = rst_file.read_text()
        assert "plotbar" not in updated

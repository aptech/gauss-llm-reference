"""Safe RST file editor with leaf-text-only constraint.

Applies FixProposals to RST files, rejecting lines inside tables,
code blocks, and directive arguments as unsafe to modify.
"""

from __future__ import annotations

import re
from pathlib import Path

from gauss_doc_qa.fixer.models import FixProposal

# Safety-check patterns for lines that should NOT be modified
TABLE_GRID_RE = re.compile(r"^\s*[+|][-=+|]+[+|]\s*$")
TABLE_SIMPLE_RE = re.compile(r"^\s*[=]+(\s+[=]+)+\s*$")
TABLE_CELL_RE = re.compile(r"^\s*\|")
DIRECTIVE_RE = re.compile(r"^\s*\.\.\s+\w+")


def compute_code_block_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """Identify line ranges that are inside code blocks.

    Detects both ``::`` literal blocks and ``.. code-block::`` directives.
    Line numbers are 1-based to match Finding.line.

    Args:
        lines: List of file lines (without trailing newlines).

    Returns:
        List of (start_line, end_line) tuples (1-based, inclusive).
    """
    ranges: list[tuple[int, int]] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.rstrip()

        # Check for :: at end of line or .. code-block:: directive
        is_literal = stripped.endswith("::") and not stripped.startswith("..")
        is_code_directive = bool(re.match(r"^\s*\.\.\s+code-block::", line))

        if is_literal or is_code_directive:
            # Skip blank lines after the marker
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1

            if j >= n:
                break

            # Determine the indentation of the code block content
            first_content = lines[j]
            indent = len(first_content) - len(first_content.lstrip())
            if indent == 0:
                # Not actually a code block (no indentation)
                i += 1
                continue

            start = j + 1  # 1-based
            end = j + 1    # 1-based

            # Consume all lines that are indented or blank
            k = j
            while k < n:
                if lines[k].strip() == "":
                    k += 1
                    continue
                current_indent = len(lines[k]) - len(lines[k].lstrip())
                if current_indent >= indent:
                    end = k + 1  # 1-based
                    k += 1
                else:
                    break

            ranges.append((start, end))
            i = k
        else:
            i += 1

    return ranges


def is_safe_to_fix(
    line: str,
    line_num: int,
    all_lines: list[str],
    code_block_ranges: list[tuple[int, int]],
) -> bool:
    """Check whether a line is safe to apply an automated fix.

    Lines inside tables, code blocks, and non-seealso directive arguments
    are rejected as unsafe to modify.

    Args:
        line: The line content.
        line_num: 1-based line number.
        all_lines: All lines in the file.
        code_block_ranges: List of (start, end) 1-based line ranges for code blocks.

    Returns:
        True if the line is safe to fix, False otherwise.
    """
    # Reject table lines
    if TABLE_GRID_RE.match(line):
        return False
    if TABLE_SIMPLE_RE.match(line):
        return False
    if TABLE_CELL_RE.match(line):
        return False

    # Reject directive lines (except seealso)
    if DIRECTIVE_RE.match(line) and "seealso" not in line:
        return False

    # Reject lines inside code blocks
    for start, end in code_block_ranges:
        if start <= line_num <= end:
            return False

    return True


def apply_fixes(
    proposals: list[FixProposal],
    dry_run: bool = True,
) -> list[FixProposal]:
    """Apply fix proposals to RST files.

    Processes proposals bottom-up within each file to preserve line numbers.
    Skips proposals on lines that are unsafe to modify.

    Args:
        proposals: List of FixProposal objects to apply.
        dry_run: If True, return proposals that would be applied without
                 modifying files. If False, write changes to disk.

    Returns:
        List of FixProposal objects that were (or would be) applied.
    """
    if not proposals:
        return []

    # Group proposals by file
    by_file: dict[str, list[FixProposal]] = {}
    for p in proposals:
        by_file.setdefault(p.file_path, []).append(p)

    applied: list[FixProposal] = []

    for file_path, file_proposals in by_file.items():
        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        lines = content.splitlines(keepends=True)
        code_ranges = compute_code_block_ranges(
            [l.rstrip("\n\r") for l in lines]
        )

        # Sort by line number descending (bottom-up for safety)
        file_proposals.sort(key=lambda p: p.line_number, reverse=True)

        modified = False
        for proposal in file_proposals:
            idx = proposal.line_number - 1  # 0-based
            if idx < 0 or idx >= len(lines):
                continue

            line_content = lines[idx].rstrip("\n\r")
            if not is_safe_to_fix(line_content, proposal.line_number, lines, code_ranges):
                continue

            applied.append(proposal)

            if not dry_run:
                # Preserve original line ending
                ending = ""
                if lines[idx].endswith("\r\n"):
                    ending = "\r\n"
                elif lines[idx].endswith("\n"):
                    ending = "\n"
                elif lines[idx].endswith("\r"):
                    ending = "\r"

                lines[idx] = proposal.fixed_text + ending
                modified = True

        if not dry_run and modified:
            Path(file_path).write_text("".join(lines), encoding="utf-8")

    return applied

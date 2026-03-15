"""Data models for the fixer module."""

from __future__ import annotations

from dataclasses import dataclass

from gauss_doc_qa.models import Finding


@dataclass
class FixProposal:
    """A proposed fix for a broken cross-reference.

    Attributes:
        file_path: Path to the RST file containing the broken reference.
        line_number: 1-based line number of the broken reference.
        original_text: The full line containing the broken ref.
        fixed_text: The line with the corrected ref.
        old_target: The broken target name (e.g., "plotbar").
        new_target: The corrected target name (e.g., "plotBar").
        category: The finding category (e.g., "broken_func_ref").
        confidence: Fuzzy match confidence score (0.0-1.0).
        finding: The original Finding that triggered this proposal.
    """

    file_path: str
    line_number: int
    original_text: str
    fixed_text: str
    old_target: str
    new_target: str
    category: str
    confidence: float
    finding: Finding

"""Glossary fixer -- converts terminology findings into FixProposals."""

from __future__ import annotations

import re
from pathlib import Path

from gauss_doc_qa.fixer.models import FixProposal
from gauss_doc_qa.glossary import GlossaryEntry, build_alias_map
from gauss_doc_qa.models import Finding

# Extract alias and canonical from message:
# "Non-canonical term '{alias}' found. Use '{canonical}' instead."
_TERM_RE = re.compile(r"'([^']+)'")


def resolve_glossary_fixes(
    findings: list[Finding],
    glossary_entries: list[GlossaryEntry],
) -> list[FixProposal]:
    """Convert GlossaryChecker 'terminology' findings into FixProposals.

    Each finding's message contains the non-canonical alias and the canonical
    form. The fixer reads the source line and replaces the alias with the
    canonical form using word-boundary-safe regex.

    Args:
        findings: List of Finding objects (only category="terminology" processed).
        glossary_entries: Glossary entries used to build the alias map.

    Returns:
        List of FixProposal objects for resolvable findings.
    """
    alias_map = build_alias_map(glossary_entries)
    proposals: list[FixProposal] = []

    for finding in findings:
        if finding.category != "terminology":
            continue

        # Parse alias and canonical from the message
        matches = _TERM_RE.findall(finding.message)
        if len(matches) < 2:
            continue
        alias = matches[0]
        canonical = matches[1]

        # Read the source file to get the original line
        if finding.line is None:
            continue

        try:
            lines = Path(finding.file).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue

        if finding.line < 1 or finding.line > len(lines):
            continue

        original_line = lines[finding.line - 1]

        # Replace the non-canonical term with the canonical form
        # Use word boundaries to prevent partial-word replacement
        pattern = re.compile(r"\b" + re.escape(alias) + r"\b")
        fixed_line = pattern.sub(canonical, original_line)

        if fixed_line == original_line:
            # No replacement happened (term not found or already canonical)
            continue

        proposals.append(FixProposal(
            file_path=finding.file,
            line_number=finding.line,
            original_text=original_line,
            fixed_text=fixed_line,
            old_target=alias,
            new_target=canonical,
            category="terminology",
            confidence=1.0,
            finding=finding,
        ))

    return proposals

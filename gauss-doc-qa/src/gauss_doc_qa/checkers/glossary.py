"""Terminology glossary checker -- flags non-canonical terms in RST files."""

from __future__ import annotations

import re

from gauss_doc_qa.checkers.base import BaseChecker
from gauss_doc_qa.glossary import GlossaryEntry, build_alias_map
from gauss_doc_qa.models import Finding, ParsedDoc, Severity


class GlossaryChecker(BaseChecker):
    """Scan RST text for non-canonical terminology.

    NOT auto-registered at import time because it requires a glossary file.
    Instantiate with a list of GlossaryEntry and call check() on parsed docs.
    """

    name = "glossary"
    requires_sphinx = False

    def __init__(self, glossary_entries: list[GlossaryEntry]) -> None:
        self._entries = glossary_entries
        self._alias_map = build_alias_map(glossary_entries)

        # Build a single combined regex for all aliases (case-insensitive).
        # Sort by length descending so longer aliases match first (e.g.,
        # "data frame" before "data").
        all_aliases = sorted(self._alias_map.keys(), key=len, reverse=True)
        if all_aliases:
            pattern = r"\b(?:" + "|".join(re.escape(a) for a in all_aliases) + r")\b"
            self._pattern = re.compile(pattern, re.IGNORECASE)
        else:
            self._pattern = None

        # Build a set of canonical terms (exact, case-sensitive) to skip
        self._canonical_forms: set[str] = {e.canonical for e in glossary_entries}

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        """Read the source file line by line and flag non-canonical terms."""
        if self._pattern is None:
            return []

        try:
            with open(parsed_doc.path, "r") as f:
                lines = f.readlines()
        except (FileNotFoundError, OSError):
            return []

        findings: list[Finding] = []
        in_code_block = False
        code_indent: int | None = None

        for line_num, line in enumerate(lines, start=1):
            stripped = line.rstrip("\n")

            # Track code block state
            if not in_code_block:
                # Detect code-block directive or implicit literal block (::)
                bare = stripped.lstrip()
                if bare.startswith(".. code-block::") or bare.startswith(".. sourcecode::"):
                    in_code_block = True
                    code_indent = None  # will be set on first indented line
                    continue
                if stripped.rstrip().endswith("::") and not bare.startswith(".."):
                    # Implicit literal block -- next indented lines are code
                    in_code_block = True
                    code_indent = None
                    continue
            else:
                # Inside a code block: skip blank lines, detect end
                bare = stripped.lstrip()
                if stripped.strip() == "":
                    continue  # blank lines within code blocks
                current_indent = len(stripped) - len(stripped.lstrip())
                if code_indent is None:
                    # First non-blank line after directive sets the indent
                    if current_indent > 0:
                        code_indent = current_indent
                        continue  # skip this code line
                    else:
                        # Non-indented line means the code block never started
                        in_code_block = False
                        # Fall through to scan this line
                else:
                    if current_indent >= code_indent:
                        continue  # still inside code block
                    else:
                        # De-indented: code block ended
                        in_code_block = False
                        # Fall through to scan this line

            # Scan the line for alias matches
            for match in self._pattern.finditer(stripped):
                matched_text = match.group(0)
                # Skip if the matched text IS the canonical form (case-sensitive)
                if matched_text in self._canonical_forms:
                    continue
                entry = self._alias_map[matched_text.lower()]
                findings.append(
                    Finding(
                        file=parsed_doc.path,
                        line=line_num,
                        severity=Severity.WARNING,
                        category="terminology",
                        checker="glossary",
                        message=f"Non-canonical term '{matched_text}' found. Use '{entry.canonical}' instead.",
                        auto_fixable=False,
                    )
                )

        return findings

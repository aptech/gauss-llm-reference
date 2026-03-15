"""See Also validator (STRC-08).

Validates that cross-reference targets inside ``.. seealso::``
directives point to existing pages and functions.
"""

from __future__ import annotations

import re
from pathlib import Path

from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import Finding, ParsedDoc, Severity

# Matches a seealso directive and captures the indented block after it
SEEALSO_RE = re.compile(
    r"^\.\.\s+seealso::\s*\n((?:[ \t]+\S[^\n]*\n?|\s*\n)*)",
    re.MULTILINE,
)

# Matches Sphinx role references like :func:`target` or :doc:`~display <target>`
ROLE_REF_RE = re.compile(r":(\w+):`~?([^`<]+?)(?:\s*<[^>]+>)?`")


class SeeAlsoChecker(BaseChecker):
    """Validate cross-references within seealso directives."""

    name = "seealso"
    requires_sphinx = True

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        findings: list[Finding] = []

        env = kwargs.get("sphinx_env")
        if env is None:
            return findings

        # Read raw RST content
        try:
            raw_rst = Path(parsed_doc.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return findings

        gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})
        gauss_objects_cf = {k.casefold(): k for k in gauss_objects}
        all_docs = env.all_docs or {}

        # Find all seealso blocks
        for sa_match in SEEALSO_RE.finditer(raw_rst):
            block = sa_match.group(1)
            # Calculate the starting line of the seealso directive
            sa_start = raw_rst[: sa_match.start()].count("\n") + 1

            for ref_match in ROLE_REF_RE.finditer(block):
                role = ref_match.group(1)
                target = ref_match.group(2).strip()

                # Calculate line number within the block
                block_offset = block[: ref_match.start()].count("\n")
                line_num = sa_start + 1 + block_offset  # +1 for directive line

                if role == "func":
                    if target.casefold() not in gauss_objects_cf:
                        findings.append(Finding(
                            file=parsed_doc.path,
                            line=line_num,
                            severity=Severity.ERROR,
                            category="broken_seealso_ref",
                            checker=self.name,
                            message=(
                                f"Broken :func: reference to '{target}' "
                                f"in seealso directive"
                            ),
                        ))

                elif role == "doc":
                    if target not in all_docs:
                        findings.append(Finding(
                            file=parsed_doc.path,
                            line=line_num,
                            severity=Severity.ERROR,
                            category="broken_seealso_ref",
                            checker=self.name,
                            message=(
                                f"Broken :doc: reference to '{target}' "
                                f"in seealso directive"
                            ),
                        ))

        return findings


register_checker(SeeAlsoChecker())

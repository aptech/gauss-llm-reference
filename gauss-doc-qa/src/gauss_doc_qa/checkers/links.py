"""Broken cross-reference checker (STRC-03).

Detects broken :func:, :doc:, and :ref: references by validating
targets against the Sphinx environment registries.
"""

from __future__ import annotations

import re
from pathlib import Path

from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import Finding, ParsedDoc, Severity

# Matches Sphinx role references like :func:`target` or :func:`~display <target>`
ROLE_REF_RE = re.compile(r":(\w+):`~?([^`<]+?)(?:\s*<[^>]+>)?`")


class LinksChecker(BaseChecker):
    """Check for broken cross-references in RST files."""

    name = "links"
    requires_sphinx = True

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        findings: list[Finding] = []

        env = kwargs.get("sphinx_env")
        if env is None:
            return findings

        # Read raw RST content from the file path
        try:
            raw_rst = Path(parsed_doc.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return findings

        gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})
        gauss_objects_cf = {k.casefold(): k for k in gauss_objects}

        all_docs = env.all_docs or {}
        std_labels = env.domaindata.get("std", {}).get("labels", {})

        for line_idx, line in enumerate(raw_rst.splitlines(), start=1):
            for match in ROLE_REF_RE.finditer(line):
                role = match.group(1)
                target = match.group(2).strip()

                if role == "func":
                    if target.casefold() not in gauss_objects_cf:
                        findings.append(Finding(
                            file=parsed_doc.path,
                            line=line_idx,
                            severity=Severity.ERROR,
                            category="broken_func_ref",
                            checker=self.name,
                            message=f"Broken :func: reference to '{target}'",
                        ))

                elif role == "doc":
                    if target not in all_docs:
                        findings.append(Finding(
                            file=parsed_doc.path,
                            line=line_idx,
                            severity=Severity.ERROR,
                            category="broken_doc_ref",
                            checker=self.name,
                            message=f"Broken :doc: reference to '{target}'",
                        ))

                elif role == "ref":
                    if target not in std_labels:
                        findings.append(Finding(
                            file=parsed_doc.path,
                            line=line_idx,
                            severity=Severity.WARNING,
                            category="broken_ref",
                            checker=self.name,
                            message=f"Broken :ref: reference to '{target}'",
                        ))

        return findings


register_checker(LinksChecker())

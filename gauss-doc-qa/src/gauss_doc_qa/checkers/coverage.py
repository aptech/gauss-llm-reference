"""Function coverage checker (STRC-07).

Detects Command Reference functions that have no code example
anywhere in the documentation corpus.
"""

from __future__ import annotations

from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import Finding, ParsedDoc, Severity


class CoverageChecker(BaseChecker):
    """Check that every registered function appears in at least one code block."""

    name = "coverage"
    requires_sphinx = True

    def __init__(self) -> None:
        self._computed = False
        self._findings: list[Finding] = []

    def _reset(self) -> None:
        """Reset cached state (useful for testing)."""
        self._computed = False
        self._findings = []

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        env = kwargs.get("sphinx_env")
        if env is None:
            return []

        if not self._computed:
            all_code_blocks = kwargs.get("all_code_blocks", {})
            self._compute_all(env, all_code_blocks)
            self._computed = True

        # Return findings matching the current parsed_doc path
        return [f for f in self._findings if f.file == parsed_doc.path]

    def _compute_all(
        self, env: object, all_code_blocks: dict[str, list[str]]
    ) -> None:
        """Check each function for presence in code blocks."""
        gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})

        # Build a single casefold'd corpus from all code block content
        corpus_parts: list[str] = []
        for blocks in all_code_blocks.values():
            for block_text in blocks:
                corpus_parts.append(block_text.casefold())
        corpus = "\n".join(corpus_parts)

        for funcname, (docname, objtype) in gauss_objects.items():
            if objtype != "function":
                continue

            if funcname.casefold() not in corpus:
                self._findings.append(Finding(
                    file=docname + ".rst",
                    line=None,
                    severity=Severity.WARNING,
                    category="uncovered_function",
                    checker=self.name,
                    message=f"Function '{funcname}' has no code example in any doc",
                ))


register_checker(CoverageChecker())

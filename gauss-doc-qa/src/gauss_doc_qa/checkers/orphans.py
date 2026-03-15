"""Orphan page detector (STRC-04).

Detects pages not reachable from the root toctree, excluding pages
marked with :orphan: metadata and include fragments.
"""

from __future__ import annotations

from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import Finding, ParsedDoc, Severity


class OrphansChecker(BaseChecker):
    """Detect pages not reachable from the root toctree."""

    name = "orphans"
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
            self._compute_all(env)
            self._computed = True

        # Return findings matching the current parsed_doc path
        return [f for f in self._findings if f.file == parsed_doc.path]

    def _compute_all(self, env: object) -> None:
        """Walk toctree from root and find orphan pages."""
        root_doc = getattr(getattr(env, "config", None), "root_doc", "index")

        # Build reachable set via recursive toctree walk
        toctree_includes = getattr(env, "toctree_includes", {}) or {}
        reachable: set[str] = set()
        self._walk_toctree(root_doc, toctree_includes, reachable)

        # Collect included fragments
        included_fragments: set[str] = set()
        env_included = getattr(env, "included", {}) or {}
        for fragments in env_included.values():
            included_fragments.update(fragments)

        # Check all docs
        all_docs = getattr(env, "all_docs", {}) or {}
        metadata = getattr(env, "metadata", {}) or {}

        for docname in all_docs:
            if docname in reachable:
                continue
            if docname in included_fragments:
                continue
            doc_meta = metadata.get(docname, {})
            if "orphan" in doc_meta:
                continue

            self._findings.append(Finding(
                file=docname + ".rst",
                line=None,
                severity=Severity.WARNING,
                category="orphan_page",
                checker=self.name,
                message="Page not reachable from any toctree",
            ))

    def _walk_toctree(
        self,
        docname: str,
        toctree_includes: dict[str, list[str]],
        reachable: set[str],
    ) -> None:
        """Recursively walk toctree to build reachable set."""
        if docname in reachable:
            return
        reachable.add(docname)
        for child in toctree_includes.get(docname, []):
            self._walk_toctree(child, toctree_includes, reachable)


register_checker(OrphansChecker())

"""Tests for the orphan page detector (orphans.py)."""

from unittest.mock import MagicMock

import pytest

from gauss_doc_qa.checkers.orphans import OrphansChecker
from gauss_doc_qa.models import DocType, ParsedDoc, Severity


def _make_parsed_doc(docname: str) -> ParsedDoc:
    """Create a ParsedDoc with path matching docname + .rst."""
    return ParsedDoc(
        path=docname + ".rst",
        doc_type=DocType.COMMAND_REF,
        title="Test",
        sections=[],
        code_blocks=[],
        field_lists=[],
        raw_doc=None,
    )


def _make_env(
    all_docs: dict | None = None,
    toctree_includes: dict | None = None,
    metadata: dict | None = None,
    included: dict | None = None,
    root_doc: str = "index",
):
    """Create a mock Sphinx environment."""
    env = MagicMock()
    env.all_docs = all_docs or {}
    env.toctree_includes = toctree_includes or {}
    env.metadata = metadata or {}
    env.included = included or {}
    env.config.root_doc = root_doc
    return env


class TestOrphansChecker:
    def setup_method(self):
        self.checker = OrphansChecker()

    def test_page_in_toctree_not_flagged(self):
        env = _make_env(
            all_docs={"index": 1, "abs": 2},
            toctree_includes={"index": ["abs"]},
        )
        doc = _make_parsed_doc("abs")
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_page_not_in_toctree_flagged(self):
        self.checker._reset()
        env = _make_env(
            all_docs={"index": 1, "orphaned_page": 2},
            toctree_includes={"index": []},
        )
        doc = _make_parsed_doc("orphaned_page")
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].severity == Severity.WARNING
        assert findings[0].category == "orphan_page"
        assert findings[0].file == "orphaned_page.rst"

    def test_orphan_metadata_not_flagged(self):
        self.checker._reset()
        env = _make_env(
            all_docs={"index": 1, "special_page": 2},
            toctree_includes={"index": []},
            metadata={"special_page": {"orphan": True}},
        )
        doc = _make_parsed_doc("special_page")
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_include_fragment_not_flagged(self):
        self.checker._reset()
        env = _make_env(
            all_docs={"index": 1, "fragment": 2},
            toctree_includes={"index": []},
            included={"index": {"fragment"}},
        )
        doc = _make_parsed_doc("fragment")
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_recursive_toctree_walk(self):
        self.checker._reset()
        env = _make_env(
            all_docs={"index": 1, "chapter1": 2, "section1a": 3, "deep_page": 4},
            toctree_includes={
                "index": ["chapter1"],
                "chapter1": ["section1a"],
                "section1a": ["deep_page"],
            },
        )
        doc = _make_parsed_doc("deep_page")
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_no_sphinx_env_returns_empty(self):
        self.checker._reset()
        doc = _make_parsed_doc("anything")
        findings = self.checker.check(doc)
        assert len(findings) == 0

    def test_caching_returns_per_file(self):
        """After computing once, only returns findings for the requested file."""
        self.checker._reset()
        env = _make_env(
            all_docs={"index": 1, "orphan_a": 2, "orphan_b": 3},
            toctree_includes={"index": []},
        )
        # First call computes all orphans
        doc_a = _make_parsed_doc("orphan_a")
        findings_a = self.checker.check(doc_a, sphinx_env=env)
        assert len(findings_a) == 1
        assert findings_a[0].file == "orphan_a.rst"

        # Second call returns only orphan_b findings
        doc_b = _make_parsed_doc("orphan_b")
        findings_b = self.checker.check(doc_b, sphinx_env=env)
        assert len(findings_b) == 1
        assert findings_b[0].file == "orphan_b.rst"

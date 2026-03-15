"""Tests for the broken cross-reference checker (links.py)."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from gauss_doc_qa.checkers.links import LinksChecker
from gauss_doc_qa.models import DocType, ParsedDoc, Severity


def _make_parsed_doc(rst_content: str) -> ParsedDoc:
    """Write RST to a temp file and return a ParsedDoc pointing to it."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".rst", delete=False)
    tmp.write(rst_content)
    tmp.flush()
    return ParsedDoc(
        path=tmp.name,
        doc_type=DocType.COMMAND_REF,
        title="Test",
        sections=[],
        code_blocks=[],
        field_lists=[],
        raw_doc=None,
    )


def _make_env():
    """Create a mock Sphinx environment with sample data."""
    env = MagicMock()
    env.domaindata = {
        "gauss": {
            "objects": {
                "abs": ("abs", "function"),
                "olsmt": ("olsmt", "function"),
            },
        },
        "std": {"labels": {"genindex": ("genindex", "", "General Index")}},
    }
    env.all_docs = {"abs": 1234, "olsmt": 1234, "index": 1234}
    return env


class TestLinksChecker:
    def setup_method(self):
        self.checker = LinksChecker()

    def test_valid_func_ref_no_finding(self):
        doc = _make_parsed_doc("See :func:`abs` for details.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_invalid_func_ref_produces_error(self):
        doc = _make_parsed_doc("See :func:`nonexistent_func` for details.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].severity == Severity.ERROR
        assert findings[0].category == "broken_func_ref"
        assert "nonexistent_func" in findings[0].message

    def test_case_insensitive_func_ref(self):
        doc = _make_parsed_doc("See :func:`ABS` for absolute value.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_valid_doc_ref_no_finding(self):
        doc = _make_parsed_doc("See :doc:`abs` for the abs page.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_invalid_doc_ref_produces_error(self):
        doc = _make_parsed_doc("See :doc:`missing_page` for details.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].severity == Severity.ERROR
        assert findings[0].category == "broken_doc_ref"
        assert "missing_page" in findings[0].message

    def test_valid_ref_label_no_finding(self):
        doc = _make_parsed_doc("See :ref:`genindex` for the index.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_invalid_ref_label_produces_warning(self):
        doc = _make_parsed_doc("See :ref:`missing_label` for details.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].severity == Severity.WARNING
        assert findings[0].category == "broken_ref"

    def test_no_sphinx_env_returns_empty(self):
        doc = _make_parsed_doc("See :func:`abs` for details.")
        findings = self.checker.check(doc)
        assert len(findings) == 0

    def test_multiple_refs_on_one_line(self):
        doc = _make_parsed_doc("See :func:`abs` and :func:`missing_fn`.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].category == "broken_func_ref"

    def test_tilde_prefix_still_validates(self):
        doc = _make_parsed_doc("See :func:`~abs` for details.")
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

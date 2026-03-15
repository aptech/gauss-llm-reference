"""Tests for the See Also validator (seealso.py)."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from gauss_doc_qa.checkers.seealso import SeeAlsoChecker
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
    env = MagicMock()
    env.domaindata = {
        "gauss": {
            "objects": {
                "abs": ("abs", "function"),
                "olsmt": ("olsmt", "function"),
            },
        },
    }
    env.all_docs = {"abs": 1234, "olsmt": 1234, "index": 1234}
    return env


class TestSeeAlsoChecker:
    def setup_method(self):
        self.checker = SeeAlsoChecker()

    def test_valid_func_in_seealso_no_finding(self):
        doc = _make_parsed_doc(
            "Title\n=====\n\n.. seealso::\n\n   :func:`abs`\n"
        )
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_invalid_func_in_seealso_produces_error(self):
        doc = _make_parsed_doc(
            "Title\n=====\n\n.. seealso::\n\n   :func:`nonexistent`\n"
        )
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].severity == Severity.ERROR
        assert findings[0].category == "broken_seealso_ref"
        assert "nonexistent" in findings[0].message

    def test_valid_doc_in_seealso_no_finding(self):
        doc = _make_parsed_doc(
            "Title\n=====\n\n.. seealso::\n\n   :doc:`abs`\n"
        )
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_invalid_doc_in_seealso_produces_error(self):
        doc = _make_parsed_doc(
            "Title\n=====\n\n.. seealso::\n\n   :doc:`missing_page`\n"
        )
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 1
        assert findings[0].severity == Severity.ERROR
        assert findings[0].category == "broken_seealso_ref"
        assert "missing_page" in findings[0].message

    def test_no_seealso_no_findings(self):
        doc = _make_parsed_doc(
            "Title\n=====\n\nJust some text with :func:`abs`.\n"
        )
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

    def test_no_sphinx_env_returns_empty(self):
        doc = _make_parsed_doc(".. seealso::\n\n   :func:`abs`\n")
        findings = self.checker.check(doc)
        assert len(findings) == 0

    def test_case_insensitive_func_in_seealso(self):
        doc = _make_parsed_doc(
            "Title\n=====\n\n.. seealso::\n\n   :func:`ABS`\n"
        )
        env = _make_env()
        findings = self.checker.check(doc, sphinx_env=env)
        assert len(findings) == 0

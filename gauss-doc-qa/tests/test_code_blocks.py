"""Tests for CodeBlockChecker (STRC-01, STRC-02)."""

import pytest

from gauss_doc_qa.checkers.code_blocks import CodeBlockChecker
from gauss_doc_qa.models import DocType, Severity
from gauss_doc_qa.parser.rst_parser import parse_rst


@pytest.fixture
def checker():
    return CodeBlockChecker()


class TestCodeBlockPresence:
    """STRC-01: COMMAND_REF and OPERATOR pages must have code blocks."""

    def test_function_page_no_findings(self, checker, function_page_rst):
        doc = parse_rst("myabs.rst", function_page_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_missing_code_block(self, checker, missing_code_rst):
        doc = parse_rst("myfunc.rst", missing_code_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        missing = [f for f in findings if f.category == "missing_code_block"]
        assert len(missing) == 1
        assert missing[0].severity == Severity.WARNING
        assert missing[0].checker == "code_blocks"

    def test_operator_page_has_code(self, checker, operator_page_rst):
        doc = parse_rst("addition.rst", operator_page_rst, DocType.OPERATOR)
        findings = checker.check(doc)
        assert len(findings) == 0


class TestCodeBlockNonEmpty:
    """STRC-02: Code blocks must not be empty or placeholder-only."""

    def test_empty_code_block(self, checker, empty_code_rst):
        doc = parse_rst("emptyfunc.rst", empty_code_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        empty = [f for f in findings if f.category == "empty_code_block"]
        assert len(empty) >= 1
        assert empty[0].severity == Severity.ERROR
        assert empty[0].checker == "code_blocks"


class TestDocTypeFiltering:
    """Checkers must skip non-applicable doc types."""

    def test_index_page_skipped(self, checker, index_page_rst):
        doc = parse_rst("A.rst", index_page_rst, DocType.ALPHA_INDEX)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_include_fragment_skipped(self, checker, include_fragment_rst):
        doc = parse_rst("_fragment.rst", include_fragment_rst, DocType.INCLUDE_FRAGMENT)
        findings = checker.check(doc)
        assert len(findings) == 0

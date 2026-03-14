"""Tests for SignatureChecker (STRC-06)."""

import pytest

from gauss_doc_qa.checkers.signatures import SignatureChecker
from gauss_doc_qa.models import DocType, Severity
from gauss_doc_qa.parser.rst_parser import parse_rst


@pytest.fixture
def checker():
    return SignatureChecker()


class TestSignatureCompleteness:
    """STRC-06: Function pages with args must have :param: documentation."""

    def test_complete_signature(self, checker, function_page_rst):
        doc = parse_rst("myabs.rst", function_page_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_incomplete_signature(self, checker, incomplete_sig_rst):
        doc = parse_rst("badsig.rst", incomplete_sig_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        incomplete = [f for f in findings if f.category == "incomplete_signature"]
        assert len(incomplete) >= 1
        assert incomplete[0].severity == Severity.WARNING
        assert incomplete[0].checker == "signatures"


class TestDocTypeFiltering:
    """Signature checker must skip non-function doc types."""

    def test_operator_skipped(self, checker, operator_page_rst):
        doc = parse_rst("addition.rst", operator_page_rst, DocType.OPERATOR)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_index_page_skipped(self, checker, index_page_rst):
        doc = parse_rst("A.rst", index_page_rst, DocType.ALPHA_INDEX)
        findings = checker.check(doc)
        assert len(findings) == 0

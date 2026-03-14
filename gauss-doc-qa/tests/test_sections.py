"""Tests for SectionChecker (STRC-05)."""

import pytest

from gauss_doc_qa.checkers.sections import SectionChecker
from gauss_doc_qa.models import DocType, Severity
from gauss_doc_qa.parser.rst_parser import parse_rst


@pytest.fixture
def checker():
    return SectionChecker()


class TestRequiredSections:
    """STRC-05: Reference pages must have Purpose, Format, Examples."""

    def test_function_page_has_all_sections(self, checker, function_page_rst):
        doc = parse_rst("myabs.rst", function_page_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_missing_sections(self, checker, missing_sections_rst):
        doc = parse_rst("incomplete.rst", missing_sections_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        # missing_sections.rst only has Purpose -- missing Format and Examples
        assert len(findings) == 2
        categories = {f.category for f in findings}
        assert categories == {"missing_section"}
        messages = {f.message for f in findings}
        assert "Missing required section: Format" in messages
        assert "Missing required section: Examples" in messages

    def test_operator_page_sections(self, checker, operator_page_rst):
        doc = parse_rst("addition.rst", operator_page_rst, DocType.OPERATOR)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_finding_has_correct_category(self, checker, missing_sections_rst):
        doc = parse_rst("incomplete.rst", missing_sections_rst, DocType.COMMAND_REF)
        findings = checker.check(doc)
        for f in findings:
            assert f.category == "missing_section"
            assert f.checker == "sections"
            assert f.severity == Severity.WARNING


class TestDocTypeFiltering:
    """Section checker must skip non-reference doc types."""

    def test_index_page_skipped(self, checker, index_page_rst):
        doc = parse_rst("A.rst", index_page_rst, DocType.ALPHA_INDEX)
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_include_fragment_skipped(self, checker, include_fragment_rst):
        doc = parse_rst("_fragment.rst", include_fragment_rst, DocType.INCLUDE_FRAGMENT)
        findings = checker.check(doc)
        assert len(findings) == 0

"""Tests for the function coverage checker (coverage.py)."""

from unittest.mock import MagicMock

import pytest

from gauss_doc_qa.checkers.coverage import CoverageChecker
from gauss_doc_qa.models import DocType, ParsedDoc, Severity


def _make_parsed_doc(docname: str) -> ParsedDoc:
    return ParsedDoc(
        path=docname + ".rst",
        doc_type=DocType.COMMAND_REF,
        title="Test",
        sections=[],
        code_blocks=[],
        field_lists=[],
        raw_doc=None,
    )


def _make_env(objects: dict | None = None):
    env = MagicMock()
    env.domaindata = {
        "gauss": {
            "objects": objects or {},
        },
    }
    return env


class TestCoverageChecker:
    def setup_method(self):
        self.checker = CoverageChecker()

    def test_function_in_code_block_no_finding(self):
        env = _make_env({"abs": ("abs", "function")})
        code_blocks = {"abs": ["x = abs(-5);"]}
        doc = _make_parsed_doc("abs")
        findings = self.checker.check(doc, sphinx_env=env, all_code_blocks=code_blocks)
        assert len(findings) == 0

    def test_function_not_in_any_code_block(self):
        self.checker._reset()
        env = _make_env({"mysteryFunc": ("mysteryFunc", "function")})
        code_blocks = {"other": ["x = abs(-5);"]}
        doc = _make_parsed_doc("mysteryFunc")
        findings = self.checker.check(
            doc, sphinx_env=env, all_code_blocks=code_blocks
        )
        assert len(findings) == 1
        assert findings[0].severity == Severity.WARNING
        assert findings[0].category == "uncovered_function"
        assert "mysteryFunc" in findings[0].message

    def test_case_insensitive_matching(self):
        self.checker._reset()
        env = _make_env({"olsmt": ("olsmt", "function")})
        code_blocks = {"example": ["result = OLSMT(data, formula);"]}
        doc = _make_parsed_doc("olsmt")
        findings = self.checker.check(
            doc, sphinx_env=env, all_code_blocks=code_blocks
        )
        assert len(findings) == 0

    def test_non_function_objects_not_checked(self):
        self.checker._reset()
        env = _make_env({
            "abs": ("abs", "function"),
            "gaussModule": ("gaussModule", "module"),
        })
        code_blocks = {"abs": ["x = abs(-5);"]}
        doc = _make_parsed_doc("abs")
        findings = self.checker.check(
            doc, sphinx_env=env, all_code_blocks=code_blocks
        )
        # Only function objects are checked; gaussModule is a module, so no finding
        assert len(findings) == 0

    def test_no_sphinx_env_returns_empty(self):
        self.checker._reset()
        doc = _make_parsed_doc("anything")
        findings = self.checker.check(doc)
        assert len(findings) == 0

    def test_empty_code_blocks_flags_all_functions(self):
        self.checker._reset()
        env = _make_env({"abs": ("abs", "function")})
        code_blocks = {}
        doc = _make_parsed_doc("abs")
        findings = self.checker.check(
            doc, sphinx_env=env, all_code_blocks=code_blocks
        )
        assert len(findings) == 1
        assert findings[0].category == "uncovered_function"

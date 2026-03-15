"""Unit tests for AI-assisted example code verification (mocked API)."""

import sys
from types import ModuleType
from unittest.mock import patch, MagicMock

import pytest

from gauss_doc_qa.deep.ai_checker import (
    ExampleCheckResult,
    ai_check_examples,
    ai_check_examples_batch,
)
from gauss_doc_qa.deep.models import DeepCheckResult, DeepCheckType, DeepFunctionResult
from gauss_doc_qa.models import CodeBlock, DocType, ParsedDoc


def _make_parsed_doc(code_blocks=None, path="/tmp/test.rst"):
    """Create a minimal ParsedDoc for testing."""
    if code_blocks is None:
        code_blocks = []
    return ParsedDoc(
        path=path,
        doc_type=DocType.COMMAND_REF,
        title="test",
        sections=[],
        code_blocks=code_blocks,
        field_lists=[],
        raw_doc=MagicMock(),
    )


def _mock_anthropic_response(has_issues, issues=None):
    """Create a mock anthropic module + client that returns given result."""
    if issues is None:
        issues = []
    mock_response = MagicMock()
    mock_response.parsed_output = ExampleCheckResult(
        has_issues=has_issues, issues=issues
    )
    mock_client = MagicMock()
    mock_client.messages.parse.return_value = mock_response

    mock_module = MagicMock()
    mock_module.Anthropic.return_value = mock_client
    return mock_module


class TestAiCheckExamplesNoIssues:

    def test_no_issues_found(self):
        """AI check with no issues returns passed=True."""
        mock_mod = _mock_anthropic_response(has_issues=False)

        parsed = _make_parsed_doc(code_blocks=[
            CodeBlock(content="x = ols(y, x_data);", line_number=10, is_empty=False),
        ])

        with patch.dict(sys.modules, {"anthropic": mock_mod}):
            result = ai_check_examples(parsed, "ols")

        assert result.check == DeepCheckType.AI_EXAMPLE_QUALITY
        assert result.passed is True
        assert result.detail == "No issues found"


class TestAiCheckExamplesWithIssues:

    def test_issues_found(self):
        """AI check with issues returns passed=False and detail text."""
        mock_mod = _mock_anthropic_response(
            has_issues=True,
            issues=[
                "Example calls meanc() instead of ols()",
                "Parameter 'order' is not a valid ols parameter",
            ],
        )

        parsed = _make_parsed_doc(code_blocks=[
            CodeBlock(content="x = meanc(y);", line_number=10, is_empty=False),
        ])

        with patch.dict(sys.modules, {"anthropic": mock_mod}):
            result = ai_check_examples(parsed, "ols")

        assert result.check == DeepCheckType.AI_EXAMPLE_QUALITY
        assert result.passed is False
        assert "meanc()" in result.detail
        assert "Parameter 'order'" in result.detail


class TestAiCheckExamplesNoCodeBlocks:

    def test_no_code_blocks(self):
        """AI check with no code blocks returns passed=True with skip message."""
        parsed = _make_parsed_doc(code_blocks=[])
        result = ai_check_examples(parsed, "ols")

        assert result.check == DeepCheckType.AI_EXAMPLE_QUALITY
        assert result.passed is True
        assert result.detail == "No examples to verify"

    def test_only_empty_code_blocks(self):
        """AI check with only empty code blocks returns passed=True."""
        parsed = _make_parsed_doc(code_blocks=[
            CodeBlock(content="", line_number=5, is_empty=True),
            CodeBlock(content="  ", line_number=10, is_empty=False),
        ])
        result = ai_check_examples(parsed, "ols")

        assert result.check == DeepCheckType.AI_EXAMPLE_QUALITY
        assert result.passed is True
        assert result.detail == "No examples to verify"


class TestAiCheckExamplesBatch:

    @patch("gauss_doc_qa.deep.ai_checker.ai_check_examples")
    @patch("gauss_doc_qa.deep.ai_checker.parse_rst")
    def test_batch_updates_overall_pass(self, mock_parse, mock_ai_check, tmp_path):
        """Batch AI check updates overall_pass based on AI result."""
        # Create a real RST file
        rst_file = tmp_path / "ols.rst"
        rst_file.write_text(".. function:: ols(y, x)\n\n   OLS regression.\n")

        mock_parse.return_value = _make_parsed_doc(
            code_blocks=[CodeBlock(content="x = ols(y, x_data);", line_number=10, is_empty=False)],
            path=str(rst_file),
        )

        # AI check finds issues
        mock_ai_check.return_value = DeepCheckResult(
            check=DeepCheckType.AI_EXAMPLE_QUALITY,
            passed=False,
            detail="Example calls wrong function",
        )

        results = [
            DeepFunctionResult(
                function_name="ols",
                doc_page="command_ref/ols",
                file_path=str(rst_file),
                checks=[
                    DeepCheckResult(
                        check=DeepCheckType.SIGNATURE_COMPLETE,
                        passed=True,
                        detail="2/2 params documented",
                    ),
                ],
                overall_pass=True,
            ),
        ]

        updated = ai_check_examples_batch(results, str(tmp_path))

        assert len(updated) == 1
        assert len(updated[0].checks) == 2
        # AI check failed, so overall should be False
        assert updated[0].overall_pass is False

    @patch("gauss_doc_qa.deep.ai_checker.ai_check_examples")
    @patch("gauss_doc_qa.deep.ai_checker.parse_rst")
    def test_batch_passes_when_all_pass(self, mock_parse, mock_ai_check, tmp_path):
        """Batch AI check keeps overall_pass=True when AI check passes."""
        rst_file = tmp_path / "meanc.rst"
        rst_file.write_text(".. function:: meanc(x)\n\n   Column means.\n")

        mock_parse.return_value = _make_parsed_doc(
            code_blocks=[CodeBlock(content="m = meanc(x);", line_number=5, is_empty=False)],
            path=str(rst_file),
        )

        mock_ai_check.return_value = DeepCheckResult(
            check=DeepCheckType.AI_EXAMPLE_QUALITY,
            passed=True,
            detail="No issues found",
        )

        results = [
            DeepFunctionResult(
                function_name="meanc",
                doc_page="command_ref/meanc",
                file_path=str(rst_file),
                checks=[
                    DeepCheckResult(
                        check=DeepCheckType.SIGNATURE_COMPLETE,
                        passed=True,
                        detail="1/1 params documented",
                    ),
                ],
                overall_pass=True,
            ),
        ]

        updated = ai_check_examples_batch(results, str(tmp_path))

        assert len(updated) == 1
        assert updated[0].overall_pass is True

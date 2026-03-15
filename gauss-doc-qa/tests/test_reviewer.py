"""Tests for the AI reviewer module with mocked API calls."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from gauss_doc_qa.models import DocType, Severity, Finding
from gauss_doc_qa.ai.personas import (
    PERSONAS,
    NEWCOMER_PERSONA,
    EXPERT_PERSONA,
    WRITER_PERSONA,
    RubricCheck,
)
from gauss_doc_qa.ai.schemas import CheckResult, PersonaReviewResponse
from gauss_doc_qa.ai.reviewer import (
    extract_doc_text,
    build_rubric_prompt,
    review_to_findings,
    run_persona_review,
)
from gauss_doc_qa.parser.rst_parser import parse_rst


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestReviewToFindings:
    """Tests for converting PersonaReviewResponse to Finding objects."""

    def test_review_to_findings_converts_failures(self):
        review = PersonaReviewResponse(
            results=[
                CheckResult(check_id="NEW-01", passed=False, evidence="No GAUSS explanation found", line_hint="Introduction"),
                CheckResult(check_id="NEW-02", passed=True, evidence="", line_hint=""),
                CheckResult(check_id="NEW-03", passed=False, evidence="Code example has no output", line_hint="First Steps"),
            ]
        )
        findings = review_to_findings(review, NEWCOMER_PERSONA, "getting_started.rst")
        assert len(findings) == 2
        assert all(isinstance(f, Finding) for f in findings)
        assert findings[0].severity == Severity.WARNING
        assert findings[0].category == "undefined_concept"
        assert findings[0].checker == "ai_newcomer"
        assert "[NEW-01]" in findings[0].message
        assert findings[1].category == "missing_output"

    def test_review_to_findings_all_pass(self):
        review = PersonaReviewResponse(
            results=[
                CheckResult(check_id="NEW-01", passed=True, evidence="", line_hint=""),
                CheckResult(check_id="NEW-02", passed=True, evidence="", line_hint=""),
            ]
        )
        findings = review_to_findings(review, NEWCOMER_PERSONA, "getting_started.rst")
        assert findings == []

    def test_review_to_findings_checker_name_format(self):
        for name, persona in PERSONAS.items():
            review = PersonaReviewResponse(
                results=[
                    CheckResult(
                        check_id=persona.rubric[0].id,
                        passed=False,
                        evidence="test",
                        line_hint="test",
                    )
                ]
            )
            findings = review_to_findings(review, persona, "test.rst")
            assert len(findings) == 1
            assert findings[0].checker == f"ai_{name}"

    def test_review_to_findings_unknown_check_id_skipped(self):
        """Unknown check IDs in the response are silently skipped."""
        review = PersonaReviewResponse(
            results=[
                CheckResult(check_id="UNKNOWN-99", passed=False, evidence="test", line_hint="test"),
            ]
        )
        findings = review_to_findings(review, NEWCOMER_PERSONA, "test.rst")
        assert findings == []

    def test_finding_has_correct_fields(self):
        review = PersonaReviewResponse(
            results=[
                CheckResult(check_id="EXP-04", passed=False, evidence="Example calls wrong func", line_hint="Examples"),
            ]
        )
        findings = review_to_findings(review, EXPERT_PERSONA, "myabs.rst")
        f = findings[0]
        assert f.file == "myabs.rst"
        assert f.line is None
        assert f.severity == Severity.ERROR
        assert f.category == "example_wrong_function"
        assert f.checker == "ai_expert"
        assert f.auto_fixable is False
        assert "Example calls wrong func" in f.message


class TestExtractDocText:
    """Tests for extracting text from parsed RST documents."""

    def test_extract_doc_text_returns_string(self):
        rst_content = (FIXTURES_DIR / "getting_started_sample.rst").read_text()
        doc = parse_rst("getting_started.rst", rst_content, DocType.GETTING_STARTED)
        text = extract_doc_text(doc, NEWCOMER_PERSONA)
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Getting Started" in text

    def test_extract_expert_focuses_sections(self):
        rst_content = (FIXTURES_DIR / "command_ref_sample.rst").read_text()
        doc = parse_rst("sampleFunc.rst", rst_content, DocType.COMMAND_REF)
        text = extract_doc_text(doc, EXPERT_PERSONA)
        assert isinstance(text, str)
        assert len(text) > 0
        # Expert extraction should include key sections
        assert "Purpose" in text or "Format" in text or "Examples" in text

    def test_extract_writer_full_text(self):
        rst_content = (FIXTURES_DIR / "user_guide_sample.rst").read_text()
        doc = parse_rst("data_handling.rst", rst_content, DocType.USER_GUIDE)
        text = extract_doc_text(doc, WRITER_PERSONA)
        assert isinstance(text, str)
        assert "Data Handling" in text


class TestBuildRubricPrompt:
    """Tests for building the rubric prompt string."""

    def test_build_rubric_prompt_includes_all_checks(self):
        prompt = build_rubric_prompt(EXPERT_PERSONA)
        for check in EXPERT_PERSONA.rubric:
            assert check.id in prompt, f"Missing check {check.id} in prompt"

    def test_build_rubric_prompt_includes_instructions(self):
        prompt = build_rubric_prompt(NEWCOMER_PERSONA)
        assert "pass" in prompt.lower() or "fail" in prompt.lower()
        assert "evidence" in prompt.lower()

    def test_build_rubric_prompt_all_personas(self):
        for name, persona in PERSONAS.items():
            prompt = build_rubric_prompt(persona)
            for check in persona.rubric:
                assert check.id in prompt


class TestRunPersonaReviewMocked:
    """Tests for run_persona_review with mocked Anthropic API."""

    def test_run_persona_review_mocked(self):
        rst_content = (FIXTURES_DIR / "getting_started_sample.rst").read_text()
        doc = parse_rst("getting_started.rst", rst_content, DocType.GETTING_STARTED)

        mock_review = PersonaReviewResponse(
            results=[
                CheckResult(
                    check_id="NEW-02",
                    passed=False,
                    evidence="'proc' used without explanation",
                    line_hint="Working with Procedures",
                ),
                CheckResult(check_id="NEW-01", passed=True, evidence="", line_hint=""),
            ]
        )

        mock_response = MagicMock()
        mock_response.parsed_output = mock_review

        mock_client = MagicMock()
        mock_client.messages.parse.return_value = mock_response

        mock_anthropic_module = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
            findings = run_persona_review(doc, NEWCOMER_PERSONA)

        assert len(findings) == 1
        assert findings[0].checker == "ai_newcomer"
        assert findings[0].category == "unexplained_term"
        assert "[NEW-02]" in findings[0].message
        assert "'proc' used without explanation" in findings[0].message

        # Verify API was called with correct parameters
        call_kwargs = mock_client.messages.parse.call_args.kwargs
        assert call_kwargs["temperature"] == 0
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_kwargs["output_format"] == PersonaReviewResponse

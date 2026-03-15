"""Tests for persona configurations and rubric validation."""

import pytest

from gauss_doc_qa.models import DocType, Severity
from gauss_doc_qa.ai.personas import (
    PERSONAS,
    NEWCOMER_PERSONA,
    EXPERT_PERSONA,
    WRITER_PERSONA,
    Persona,
    RubricCheck,
)


class TestPersonaRegistry:
    """Tests for the PERSONAS dict and persona existence."""

    def test_all_personas_exist(self):
        assert set(PERSONAS.keys()) == {"newcomer", "expert", "writer"}

    def test_personas_are_persona_instances(self):
        for p in PERSONAS.values():
            assert isinstance(p, Persona)


class TestNewcomerPersona:
    """Tests for the newcomer persona configuration."""

    def test_newcomer_targets_getting_started(self):
        assert NEWCOMER_PERSONA.target_doc_types == [DocType.GETTING_STARTED]

    def test_newcomer_has_6_checks(self):
        assert len(NEWCOMER_PERSONA.rubric) == 6

    def test_newcomer_check_ids_start_with_new(self):
        for check in NEWCOMER_PERSONA.rubric:
            assert check.id.startswith("NEW-")


class TestExpertPersona:
    """Tests for the expert persona configuration."""

    def test_expert_targets_command_ref(self):
        assert EXPERT_PERSONA.target_doc_types == [DocType.COMMAND_REF]

    def test_expert_has_7_checks(self):
        assert len(EXPERT_PERSONA.rubric) == 7

    def test_expert_check_ids_start_with_exp(self):
        for check in EXPERT_PERSONA.rubric:
            assert check.id.startswith("EXP-")


class TestWriterPersona:
    """Tests for the writer persona configuration."""

    def test_writer_targets_user_guide(self):
        assert WRITER_PERSONA.target_doc_types == [DocType.USER_GUIDE]

    def test_writer_has_6_checks(self):
        assert len(WRITER_PERSONA.rubric) == 6

    def test_writer_check_ids_start_with_wrt(self):
        for check in WRITER_PERSONA.rubric:
            assert check.id.startswith("WRT-")


class TestRubricValidation:
    """Cross-persona validation of rubric check properties."""

    def test_rubric_check_ids_unique(self):
        for name, persona in PERSONAS.items():
            ids = [check.id for check in persona.rubric]
            assert len(ids) == len(set(ids)), f"Duplicate check IDs in {name}"

    def test_rubric_checks_have_required_fields(self):
        for name, persona in PERSONAS.items():
            for check in persona.rubric:
                assert isinstance(check, RubricCheck)
                assert check.id, f"Empty id in {name}"
                assert check.question, f"Empty question in {name}"
                assert check.category, f"Empty category in {name}"
                assert isinstance(check.fail_severity, Severity), (
                    f"Invalid severity in {name}/{check.id}"
                )

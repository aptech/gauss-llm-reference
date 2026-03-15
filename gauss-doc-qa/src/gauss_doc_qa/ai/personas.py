"""Persona definitions with binary rubric checks for AI documentation review."""

from dataclasses import dataclass, field

from gauss_doc_qa.models import DocType, Severity


@dataclass
class RubricCheck:
    """A single binary pass/fail check in a persona's rubric."""

    id: str
    question: str
    fail_severity: Severity
    category: str


@dataclass
class Persona:
    """An AI reviewer persona with target doc types and a rubric of binary checks."""

    name: str
    description: str
    target_doc_types: list[DocType]
    rubric: list[RubricCheck]
    model: str = "claude-sonnet-4-20250514"


NEWCOMER_PERSONA = Persona(
    name="newcomer",
    description=(
        "You are a programmer learning GAUSS for the first time. "
        "You know Python and R but have never used GAUSS. "
        "Evaluate this Getting Started documentation page."
    ),
    target_doc_types=[DocType.GETTING_STARTED],
    rubric=[
        RubricCheck(
            "NEW-01",
            "Does the page explain what GAUSS is before using it?",
            Severity.WARNING,
            "undefined_concept",
        ),
        RubricCheck(
            "NEW-02",
            "Are all GAUSS-specific terms (e.g., 'proc', 'retp', 'endp') explained on first use?",
            Severity.WARNING,
            "unexplained_term",
        ),
        RubricCheck(
            "NEW-03",
            "Does each code example show expected output or explain what it produces?",
            Severity.WARNING,
            "missing_output",
        ),
        RubricCheck(
            "NEW-04",
            "Are prerequisite steps (installation, file paths) mentioned before code that depends on them?",
            Severity.ERROR,
            "missing_prerequisite",
        ),
        RubricCheck(
            "NEW-05",
            "Can the examples be followed in order without skipping steps?",
            Severity.WARNING,
            "broken_sequence",
        ),
        RubricCheck(
            "NEW-06",
            "Are there any references to features not yet introduced at this point in the docs?",
            Severity.INFO,
            "forward_reference",
        ),
    ],
    model="claude-sonnet-4-20250514",
)

EXPERT_PERSONA = Persona(
    name="expert",
    description=(
        "You are an experienced GAUSS developer reviewing Command Reference documentation. "
        "You care about accuracy: correct signatures, matching parameter docs, return type "
        "documentation, and working examples."
    ),
    target_doc_types=[DocType.COMMAND_REF],
    rubric=[
        RubricCheck(
            "EXP-01",
            "Does the Format section contain a function signature that matches the function directive?",
            Severity.ERROR,
            "signature_mismatch",
        ),
        RubricCheck(
            "EXP-02",
            "Does the signature list all parameters described in the parameter documentation?",
            Severity.ERROR,
            "param_mismatch",
        ),
        RubricCheck(
            "EXP-03",
            "Is the return type documented?",
            Severity.WARNING,
            "missing_return_type",
        ),
        RubricCheck(
            "EXP-04",
            "Does the example code actually call the function being documented?",
            Severity.ERROR,
            "example_wrong_function",
        ),
        RubricCheck(
            "EXP-05",
            "Are the parameter types specified (matrix, scalar, string, etc.)?",
            Severity.WARNING,
            "missing_param_types",
        ),
        RubricCheck(
            "EXP-06",
            "Does the Purpose section accurately describe what the function does?",
            Severity.WARNING,
            "misleading_purpose",
        ),
        RubricCheck(
            "EXP-07",
            "Are edge cases or special values (empty matrix, scalar input) documented?",
            Severity.INFO,
            "missing_edge_cases",
        ),
    ],
    model="claude-sonnet-4-20250514",
)

WRITER_PERSONA = Persona(
    name="writer",
    description=(
        "You are a technical writer reviewing GAUSS User Guide documentation. "
        "You focus on clarity, concept ordering, and consistent terminology."
    ),
    target_doc_types=[DocType.USER_GUIDE],
    rubric=[
        RubricCheck(
            "WRT-01",
            "Are all GAUSS-specific terms defined before or at first use?",
            Severity.WARNING,
            "undefined_term",
        ),
        RubricCheck(
            "WRT-02",
            "Are prerequisite concepts introduced before sections that use them?",
            Severity.ERROR,
            "concept_ordering",
        ),
        RubricCheck(
            "WRT-03",
            "Does each section build on the previous one without unexplained jumps?",
            Severity.WARNING,
            "missing_transition",
        ),
        RubricCheck(
            "WRT-04",
            "Are acronyms and abbreviations expanded on first use?",
            Severity.WARNING,
            "unexpanded_acronym",
        ),
        RubricCheck(
            "WRT-05",
            "Are cross-references to other documentation sections provided where relevant?",
            Severity.INFO,
            "missing_cross_ref",
        ),
        RubricCheck(
            "WRT-06",
            "Is the reading level consistent throughout (not mixing beginner and advanced without signposting)?",
            Severity.INFO,
            "inconsistent_level",
        ),
    ],
    model="claude-sonnet-4-20250514",
)

PERSONAS: dict[str, Persona] = {
    "newcomer": NEWCOMER_PERSONA,
    "expert": EXPERT_PERSONA,
    "writer": WRITER_PERSONA,
}

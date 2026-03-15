"""AI Persona Checker -- wraps persona reviews as a BaseChecker."""

from __future__ import annotations

from gauss_doc_qa.checkers.base import BaseChecker
from gauss_doc_qa.models import ParsedDoc, Finding


class AIPersonaChecker(BaseChecker):
    """Checker that runs AI persona reviews via the Claude API.

    Unlike fast/sphinx checkers, this requires an API key and is
    registered lazily (only when the CLI ``review`` command is used).
    """

    name: str = "ai_personas"
    requires_sphinx: bool = False
    requires_api: bool = True

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        """Run persona review(s) on a parsed document.

        Keyword Args:
            persona_name: Name of persona to run ("newcomer", "expert",
                "writer") or "all" (default).
            sample_size: Number of Command Reference pages to sample for
                the expert persona (default 20).
        """
        persona_name: str = kwargs.get("persona_name", "all")

        # Lazy imports to avoid loading anthropic/personas at CLI startup
        from gauss_doc_qa.ai.personas import PERSONAS
        from gauss_doc_qa.ai.reviewer import run_persona_review

        if persona_name == "all":
            personas_to_run = list(PERSONAS.values())
        else:
            if persona_name not in PERSONAS:
                return []
            personas_to_run = [PERSONAS[persona_name]]

        all_findings: list[Finding] = []
        for persona in personas_to_run:
            if parsed_doc.doc_type not in persona.target_doc_types:
                continue
            findings = run_persona_review(parsed_doc, persona)
            all_findings.extend(findings)

        return all_findings

"""Section structure checker (STRC-05).

Validates that documentation pages contain the required sections for
their doc type.  COMMAND_REF, OPERATOR, and APP_MODULE pages must have
Purpose, Format, and Examples sections.
"""

from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import ParsedDoc, Finding, Severity, DocType


class SectionChecker(BaseChecker):
    """Check that required sections are present for each doc type."""

    name = "sections"
    requires_sphinx = False

    REQUIRED_SECTIONS: dict[DocType, list[str]] = {
        DocType.COMMAND_REF: ["purpose", "format", "examples"],
        DocType.OPERATOR: ["purpose", "format", "examples"],
        # APP_MODULE excluded — mix of function refs, guides, and index pages
    }

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        findings: list[Finding] = []

        required = self.REQUIRED_SECTIONS.get(parsed_doc.doc_type)
        if required is None:
            return findings

        present = set(parsed_doc.sections)
        for section in required:
            if section not in present:
                findings.append(Finding(
                    file=parsed_doc.path,
                    line=None,
                    severity=Severity.WARNING,
                    category="missing_section",
                    checker="sections",
                    message=f"Missing required section: {section.title()}",
                ))

        return findings


register_checker(SectionChecker())

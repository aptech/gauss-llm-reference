from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import ParsedDoc, Finding, Severity, DocType


class CodeBlockChecker(BaseChecker):
    """Check code block presence (STRC-01) and non-emptiness (STRC-02).

    STRC-01: COMMAND_REF, OPERATOR, and APP_MODULE pages must have at
    least one code block.

    STRC-02: No code block should be empty or contain only whitespace /
    placeholder content.
    """

    name = "code_blocks"
    requires_sphinx = False

    # Content patterns treated as effectively empty (placeholder text)
    _PLACEHOLDER_PATTERNS = frozenset({"...", "# TODO", "TODO", "pass"})

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        findings: list[Finding] = []

        # Skip doc types that don't require code blocks
        if parsed_doc.doc_type in (
            DocType.ALPHA_INDEX,
            DocType.INCLUDE_FRAGMENT,
            DocType.GETTING_STARTED,
            DocType.USER_GUIDE,
            DocType.GRAPHICS_GUIDE,
            DocType.APP_MODULE,  # mix of function refs, guides, index pages
            DocType.OTHER,
        ):
            return findings

        # STRC-01: Must have at least one code block
        if not parsed_doc.code_blocks:
            findings.append(Finding(
                file=parsed_doc.path,
                line=None,
                severity=Severity.WARNING,
                category="missing_code_block",
                checker="code_blocks",
                message="Command/operator page has no code blocks",
            ))

        # STRC-02: No empty or placeholder-only code blocks
        for block in parsed_doc.code_blocks:
            stripped = block.content.strip()
            if block.is_empty or stripped in self._PLACEHOLDER_PATTERNS:
                findings.append(Finding(
                    file=parsed_doc.path,
                    line=block.line_number,
                    severity=Severity.ERROR,
                    category="empty_code_block",
                    checker="code_blocks",
                    message="Code block is empty or whitespace-only",
                ))

        return findings


register_checker(CodeBlockChecker())

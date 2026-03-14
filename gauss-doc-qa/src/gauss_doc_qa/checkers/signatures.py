# Stub -- implemented in Task 2
from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import ParsedDoc, Finding, Severity, DocType


class SignatureChecker(BaseChecker):
    name = "signatures"
    requires_sphinx = False

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        return []


register_checker(SignatureChecker())

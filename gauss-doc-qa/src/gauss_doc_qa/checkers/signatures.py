"""Signature completeness checker (STRC-06).

Validates that function pages with arguments document all parameters
and return values via :param: and :return:/:rtype: field entries.
"""

import re

from docutils import nodes

from gauss_doc_qa.checkers.base import BaseChecker, register_checker
from gauss_doc_qa.models import ParsedDoc, Finding, Severity, DocType


class SignatureChecker(BaseChecker):
    """Check function signature completeness on reference pages."""

    name = "signatures"
    requires_sphinx = False

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        findings: list[Finding] = []

        # Only applies to function reference pages
        if parsed_doc.doc_type not in (DocType.COMMAND_REF, DocType.APP_MODULE):
            return findings

        has_params_in_sig = self._signature_has_args(parsed_doc)
        has_param_fields = any(
            f["name"].startswith("param ") for f in parsed_doc.field_lists
        )
        has_return_fields = any(
            f["name"].startswith("return") or f["name"].startswith("rtype")
            for f in parsed_doc.field_lists
        )

        if has_params_in_sig and not has_param_fields:
            findings.append(Finding(
                file=parsed_doc.path,
                line=None,
                severity=Severity.WARNING,
                category="incomplete_signature",
                checker="signatures",
                message="Function has arguments but no :param: documentation",
            ))

        if has_param_fields and not has_return_fields:
            findings.append(Finding(
                file=parsed_doc.path,
                line=None,
                severity=Severity.INFO,
                category="missing_return_type",
                checker="signatures",
                message="Function has :param: fields but no :return: or :rtype: documentation",
            ))

        return findings

    def _signature_has_args(self, parsed_doc: ParsedDoc) -> bool:
        """Detect whether the function directive has arguments in its signature.

        Since standalone docutils treats ``.. function::`` as an unknown
        directive, the signature text ends up inside a literal_block
        child of a system_message node.  We extract the function
        signature from that text and check for non-empty parentheses.
        """
        # Search system_message literal_blocks for function directive signatures
        for sys_msg in parsed_doc.raw_doc.findall(nodes.system_message):
            for lb in sys_msg.findall(nodes.literal_block):
                text = lb.astext()
                match = re.search(r"\.\.\s+function::\s*(.+)", text)
                if match:
                    sig = match.group(1).strip()
                    # Check for non-empty parentheses
                    paren_match = re.search(r"\((.+)\)", sig)
                    if paren_match:
                        return True
                    # Empty parens or no parens -- no args
                    return False

        # No function directive found -- not a function page
        return False


register_checker(SignatureChecker())

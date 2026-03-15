"""Fixer module for auto-correcting broken cross-references."""

from gauss_doc_qa.fixer.models import FixProposal
from gauss_doc_qa.fixer.resolver import resolve_fixes, resolve_func_ref
from gauss_doc_qa.fixer.applier import apply_fixes, is_safe_to_fix
from gauss_doc_qa.fixer.verify import verify_sphinx_build

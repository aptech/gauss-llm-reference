from __future__ import annotations

from gauss_doc_qa.models import ParsedDoc, Finding


class BaseChecker:
    """Base class for all documentation quality checkers."""

    name: str = ""
    requires_sphinx: bool = False

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        raise NotImplementedError


_checkers: dict[str, BaseChecker] = {}


def register_checker(checker: BaseChecker) -> None:
    """Register a checker instance by name."""
    _checkers[checker.name] = checker


def get_checker(name: str) -> BaseChecker:
    """Get a registered checker by name."""
    return _checkers[name]


def get_all_fast_checkers() -> list[BaseChecker]:
    """Return all checkers that do not require Sphinx."""
    return [c for c in _checkers.values() if not c.requires_sphinx]


def get_all_sphinx_checkers() -> list[BaseChecker]:
    """Return all checkers that require Sphinx environment."""
    return [c for c in _checkers.values() if c.requires_sphinx]


def get_all_api_checkers() -> list[BaseChecker]:
    """Return all checkers that require API access."""
    return [c for c in _checkers.values() if getattr(c, 'requires_api', False)]

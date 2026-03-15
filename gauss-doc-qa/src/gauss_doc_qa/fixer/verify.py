"""Sphinx build verification for applied fixes.

Runs a Sphinx build and captures warnings to verify that fixes
did not introduce new problems.
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

try:
    from sphinx.application import Sphinx as _Sphinx
except ImportError:
    _Sphinx = None  # type: ignore[assignment,misc]


def _get_sphinx_cls():
    """Return the Sphinx application class, raising if unavailable."""
    if _Sphinx is None:
        raise ImportError(
            "sphinx is required for build verification. "
            "Install it with: pip install sphinx"
        )
    return _Sphinx


def verify_sphinx_build(docs_dir: str) -> dict:
    """Run a Sphinx build and capture warnings.

    Args:
        docs_dir: Path to the Sphinx docs directory (contains conf.py).

    Returns:
        Dict with keys:
            - success (bool): True if build completed without errors.
            - warning_count (int): Number of warnings produced.
            - warnings (list[str]): List of warning messages.
    """
    Sphinx = _get_sphinx_cls()

    srcdir = str(Path(docs_dir).resolve())
    outdir = tempfile.mkdtemp(prefix="gauss-qa-verify-")
    doctreedir = tempfile.mkdtemp(prefix="gauss-qa-verify-doctrees-")

    warning_stream = io.StringIO()

    try:
        app = Sphinx(
            srcdir=srcdir,
            confdir=srcdir,
            outdir=outdir,
            doctreedir=doctreedir,
            buildername="dummy",
            freshenv=True,
            warning=warning_stream,
        )
        app.build()
        success = app.statuscode == 0
    except Exception:
        success = False

    warning_text = warning_stream.getvalue()
    warnings = [
        line.strip()
        for line in warning_text.splitlines()
        if line.strip()
    ]

    return {
        "success": success,
        "warning_count": len(warnings),
        "warnings": warnings,
    }

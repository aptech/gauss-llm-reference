"""Sphinx environment loader for cross-reference validation."""

import tempfile
from pathlib import Path

from sphinx.application import Sphinx


def load_sphinx_env(docs_dir: str):
    """Load the Sphinx build environment with the GAUSS domain using the dummy builder.

    Args:
        docs_dir: Path to the Sphinx docs directory (contains conf.py).

    Returns:
        The Sphinx BuildEnvironment with resolved references, toctree data,
        and GAUSS domain object registry.
    """
    srcdir = str(Path(docs_dir).resolve())
    outdir = tempfile.mkdtemp(prefix="gauss-qa-build-")
    doctreedir = tempfile.mkdtemp(prefix="gauss-qa-doctrees-")

    app = Sphinx(
        srcdir=srcdir,
        confdir=srcdir,
        outdir=outdir,
        doctreedir=doctreedir,
        buildername="dummy",
        freshenv=True,
    )
    app.build()
    return app.env

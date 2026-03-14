import ast
import os
import re
from fnmatch import fnmatch
from pathlib import Path

from gauss_doc_qa.models import DocType
from gauss_doc_qa.parser.classifier import classify_doc


# Default exclude patterns from GAUSS conf.py
_DEFAULT_EXCLUDES = [
    "dbnomics_datasets*.rst",
    "dbnomics_series_*.rst",
    "dbnomics_last_updates.rst",
    "dbnomics_list_providers.rst",
    "dbnomics_provider.rst",
    "fred_category*.rst",
    "fred_release*.rst",
    "fred_series*.rst",
    "fred_tags*.rst",
    "fred_source*.rst",
    "fred_related*.rst",
]


def load_exclude_patterns(conf_py_path: str) -> list[str]:
    """Extract exclude_patterns list from a Sphinx conf.py file.

    Reads conf.py, finds the exclude_patterns assignment, and parses
    the list value using ast.literal_eval.

    Falls back to default exclude list if conf.py cannot be parsed.
    """
    try:
        content = Path(conf_py_path).read_text()
        # Find the exclude_patterns assignment -- may span multiple lines
        match = re.search(
            r"exclude_patterns\s*=\s*(\[.*?\])",
            content,
            re.DOTALL,
        )
        if match:
            return ast.literal_eval(match.group(1))
    except (OSError, ValueError, SyntaxError):
        pass
    return list(_DEFAULT_EXCLUDES)


def scan_docs_dir(
    docs_dir: str,
    exclude_patterns: list[str] | None = None,
) -> list[tuple[str, DocType]]:
    """Scan a docs directory for RST files, classify each one.

    Args:
        docs_dir: Path to the documentation directory.
        exclude_patterns: List of fnmatch patterns for filenames to exclude.
            If None, uses default patterns from GAUSS conf.py.

    Returns:
        List of (filepath, DocType) tuples sorted by filepath.
    """
    if exclude_patterns is None:
        exclude_patterns = list(_DEFAULT_EXCLUDES)

    results: list[tuple[str, DocType]] = []

    for root, _dirs, files in os.walk(docs_dir):
        for filename in files:
            if not filename.endswith(".rst"):
                continue

            # Check exclude patterns against filename only
            if any(fnmatch(filename, pat) for pat in exclude_patterns):
                continue

            filepath = os.path.join(root, filename)
            doc_type = classify_doc(filepath, docs_dir)
            results.append((filepath, doc_type))

    results.sort(key=lambda x: x[0])
    return results

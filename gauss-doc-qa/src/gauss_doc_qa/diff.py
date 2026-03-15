"""Diff-mode filtering for incremental scans.

Provides functions to filter a file list down to only files changed
since a given date or SVN revision.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime

from gauss_doc_qa.models import DocType


def parse_since(value: str) -> tuple[str, datetime | int]:
    """Parse a --since value into a mode and typed value.

    Args:
        value: Either a date string (YYYY-MM-DD) or SVN revision (rNNNNN).

    Returns:
        Tuple of ("date", datetime) or ("svn", int).

    Raises:
        ValueError: If value doesn't match either format.
    """
    # Check for SVN revision: r or R followed by digits
    svn_match = re.fullmatch(r"[rR](\d+)", value)
    if svn_match:
        return ("svn", int(svn_match.group(1)))

    # Check for date: YYYY-MM-DD
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return ("date", dt)
    except ValueError:
        pass

    raise ValueError(
        "--since must be a date (YYYY-MM-DD) or SVN revision (rNNNNN)"
    )


def filter_by_date(
    file_list: list[tuple[str, DocType]],
    cutoff: datetime,
) -> list[tuple[str, DocType]]:
    """Filter file list to only files modified on or after cutoff date.

    Args:
        file_list: List of (filepath, DocType) tuples from scan_docs_dir.
        cutoff: Only include files with mtime >= this datetime.

    Returns:
        Filtered list preserving original order.
    """
    cutoff_ts = cutoff.timestamp()
    return [
        (filepath, doc_type)
        for filepath, doc_type in file_list
        if os.path.getmtime(filepath) >= cutoff_ts
    ]


def filter_by_svn_revision(
    file_list: list[tuple[str, DocType]],
    revision: int,
    docs_dir: str,
) -> list[tuple[str, DocType]]:
    """Filter file list to only files changed since an SVN revision.

    Runs ``svn diff --summarize -r {revision}:HEAD`` and keeps only
    files that appear in the output.

    Args:
        file_list: List of (filepath, DocType) tuples from scan_docs_dir.
        revision: SVN revision number to diff from.
        docs_dir: Path to the docs directory (SVN working copy).

    Returns:
        Filtered list preserving original order.

    Raises:
        RuntimeError: If svn command fails or is not installed.
    """
    try:
        result = subprocess.run(
            ["svn", "diff", "--summarize", "-r", f"{revision}:HEAD", docs_dir],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("svn command not found")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr) from exc

    # Parse svn diff --summarize output.
    # Each line: status-chars whitespace absolute-path
    changed_paths: set[str] = set()
    for line in result.stdout.strip().splitlines():
        # Split on whitespace after status chars
        parts = line.split()
        if len(parts) >= 2:
            changed_paths.add(parts[-1])

    return [
        (filepath, doc_type)
        for filepath, doc_type in file_list
        if filepath in changed_paths
    ]

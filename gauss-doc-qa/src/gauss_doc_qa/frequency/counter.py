"""Cross-reference counter for GAUSS documentation.

Scans all RST files for :func: role references and counts how often
each known function is referenced from other pages.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# Same regex pattern used by the links checker
ROLE_REF_RE = re.compile(r":(\w+):`~?([^`<]+?)(?:\s*<[^>]+>)?`")


def count_crossrefs(docs_dir: str, env) -> dict[str, int]:
    """Scan all RST files for :func: references and count per function.

    Args:
        docs_dir: Path to the Sphinx documentation directory.
        env: Sphinx BuildEnvironment with domaindata['gauss']['objects'].

    Returns:
        Dict mapping function_name -> reference_count.
        Only counts references to functions registered in the GAUSS domain.
        Self-references (a function's own page referencing itself) are excluded.
    """
    gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})
    if not gauss_objects:
        return {}

    # Build case-folded lookup: casefold_name -> (canonical_name, docname)
    func_lookup: dict[str, tuple[str, str]] = {}
    for func_name, (docname, _obj_type) in gauss_objects.items():
        func_lookup[func_name.casefold()] = (func_name, docname)

    counts: dict[str, int] = {name: 0 for name in gauss_objects}
    docs_path = Path(docs_dir).resolve()

    for root, _dirs, files in os.walk(docs_dir):
        for filename in files:
            if not filename.endswith(".rst"):
                continue

            filepath = os.path.join(root, filename)

            # Compute the docname for this RST file (relative, no extension)
            try:
                rel = Path(filepath).resolve().relative_to(docs_path)
            except ValueError:
                continue
            file_docname = str(rel.with_suffix(""))

            try:
                content = Path(filepath).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for line in content.splitlines():
                for match in ROLE_REF_RE.finditer(line):
                    role = match.group(1)
                    if role != "func":
                        continue

                    target = match.group(2).strip().casefold()
                    if target not in func_lookup:
                        continue

                    canonical_name, func_docname = func_lookup[target]

                    # Exclude self-references
                    if file_docname == func_docname:
                        continue

                    counts[canonical_name] += 1

    return counts

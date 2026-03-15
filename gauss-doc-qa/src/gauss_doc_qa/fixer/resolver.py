"""Resolve broken cross-references via fuzzy matching against known GAUSS objects."""

from __future__ import annotations

import difflib
import re
from pathlib import Path

from gauss_doc_qa.fixer.models import FixProposal
from gauss_doc_qa.models import Finding

# Categories that the resolver can attempt to fix
FIXABLE_CATEGORIES = {"broken_func_ref", "broken_seealso_ref", "broken_doc_ref", "broken_ref"}

# Extract the target name from a Finding message like "Broken :func: reference to 'plotbar'"
TARGET_FROM_MSG_RE = re.compile(r"'([^']+)'")


def resolve_func_ref(
    broken_target: str,
    known_names: list[str],
    min_confidence: float = 0.85,
) -> tuple[str, float] | None:
    """Attempt to resolve a broken function reference via fuzzy matching.

    Args:
        broken_target: The broken target name to resolve.
        known_names: List of known valid function/object names.
        min_confidence: Minimum similarity ratio to accept a match.

    Returns:
        A tuple of (corrected_name, confidence_score) if a single unambiguous
        match is found, or None if no match or ambiguous.
    """
    if not known_names:
        return None

    # Build case-insensitive lookup: casefolded -> original name
    cf_to_original: dict[str, str] = {}
    cf_names: list[str] = []
    for name in known_names:
        cf = name.casefold()
        cf_to_original[cf] = name
        cf_names.append(cf)

    broken_cf = broken_target.casefold()

    matches = difflib.get_close_matches(broken_cf, cf_names, n=3, cutoff=min_confidence)

    if not matches:
        return None

    if len(matches) == 1:
        score = difflib.SequenceMatcher(None, broken_cf, matches[0]).ratio()
        return (cf_to_original[matches[0]], score)

    # Multiple matches: check if top match is clearly better
    scores = [
        difflib.SequenceMatcher(None, broken_cf, m).ratio()
        for m in matches
    ]

    if scores[0] - scores[1] > 0.05:
        return (cf_to_original[matches[0]], scores[0])

    # Ambiguous: top matches are too close
    return None


def resolve_doc_ref(
    broken_target: str,
    known_docs: list[str],
    min_confidence: float = 0.85,
) -> tuple[str, float] | None:
    """Attempt to resolve a broken :doc: reference via fuzzy matching.

    Args:
        broken_target: The broken doc target path to resolve.
        known_docs: List of known valid document paths (keys of env.all_docs).
        min_confidence: Minimum similarity ratio to accept a match.

    Returns:
        A tuple of (corrected_path, confidence_score) if a single unambiguous
        match is found, or None if no match or ambiguous.
    """
    if not known_docs:
        return None

    # Build case-insensitive lookup: casefolded -> original
    cf_to_original: dict[str, str] = {}
    cf_docs: list[str] = []
    for doc in known_docs:
        cf = doc.casefold()
        cf_to_original[cf] = doc
        cf_docs.append(cf)

    broken_cf = broken_target.casefold()

    matches = difflib.get_close_matches(broken_cf, cf_docs, n=3, cutoff=min_confidence)

    if not matches:
        return None

    if len(matches) == 1:
        score = difflib.SequenceMatcher(None, broken_cf, matches[0]).ratio()
        return (cf_to_original[matches[0]], score)

    # Multiple matches: check if top match is clearly better
    scores = [
        difflib.SequenceMatcher(None, broken_cf, m).ratio()
        for m in matches
    ]

    if scores[0] - scores[1] > 0.05:
        return (cf_to_original[matches[0]], scores[0])

    # Ambiguous: top matches are too close
    return None


def resolve_ref_ref(
    broken_target: str,
    known_labels: list[str],
    min_confidence: float = 0.80,
) -> tuple[str, float] | None:
    """Attempt to resolve a broken :ref: reference via fuzzy matching.

    Args:
        broken_target: The broken ref label to resolve.
        known_labels: List of known valid ref labels (keys of std domain labels).
        min_confidence: Minimum similarity ratio to accept a match (lower than
            func/doc since labels often have prefixes/suffixes).

    Returns:
        A tuple of (corrected_label, confidence_score) if a single unambiguous
        match is found, or None if no match or ambiguous.
    """
    if not known_labels:
        return None

    # Build case-insensitive lookup: casefolded -> original
    cf_to_original: dict[str, str] = {}
    cf_labels: list[str] = []
    for label in known_labels:
        cf = label.casefold()
        cf_to_original[cf] = label
        cf_labels.append(cf)

    broken_cf = broken_target.casefold()

    matches = difflib.get_close_matches(broken_cf, cf_labels, n=3, cutoff=min_confidence)

    if not matches:
        return None

    if len(matches) == 1:
        score = difflib.SequenceMatcher(None, broken_cf, matches[0]).ratio()
        return (cf_to_original[matches[0]], score)

    # Multiple matches: check if top match is clearly better
    scores = [
        difflib.SequenceMatcher(None, broken_cf, m).ratio()
        for m in matches
    ]

    if scores[0] - scores[1] > 0.05:
        return (cf_to_original[matches[0]], scores[0])

    # Ambiguous: top matches are too close
    return None


def resolve_fixes(
    findings: list[Finding],
    gauss_objects: dict,
    min_confidence: float = 0.85,
    doc_names: list[str] | None = None,
    label_names: list[str] | None = None,
) -> list[FixProposal]:
    """Convert broken-ref Findings into FixProposals via fuzzy matching.

    Args:
        findings: List of Finding objects from checkers.
        gauss_objects: Dict of known GAUSS domain objects (name -> info).
        min_confidence: Minimum similarity ratio to accept a match.
        doc_names: List of known document paths (keys of env.all_docs).
        label_names: List of known ref labels (keys of std domain labels).

    Returns:
        List of FixProposal objects for resolvable findings.
    """
    known_names = list(gauss_objects.keys())
    proposals: list[FixProposal] = []

    for finding in findings:
        if finding.category not in FIXABLE_CATEGORIES:
            continue

        # Extract the broken target from the message
        msg_match = TARGET_FROM_MSG_RE.search(finding.message)
        if not msg_match:
            continue
        broken_target = msg_match.group(1)

        # Route to the appropriate resolver based on category
        result: tuple[str, float] | None = None
        role: str = "func"

        if finding.category in ("broken_func_ref", "broken_seealso_ref"):
            result = resolve_func_ref(broken_target, known_names, min_confidence)
            role = "func"
        elif finding.category == "broken_doc_ref":
            if doc_names is not None:
                result = resolve_doc_ref(broken_target, doc_names, min_confidence)
            role = "doc"
        elif finding.category == "broken_ref":
            if label_names is not None:
                result = resolve_ref_ref(broken_target, label_names, min_confidence)
            role = "ref"

        if result is None:
            continue

        new_target, confidence = result

        # Read the source file to get the original line
        if finding.line is None:
            continue

        try:
            lines = Path(finding.file).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue

        if finding.line < 1 or finding.line > len(lines):
            continue

        original_line = lines[finding.line - 1]

        # Replace the old target with the new target in :role:`...` patterns
        # Match :role:`old_target` or :role:`~old_target`
        pattern = re.compile(
            r"(:" + re.escape(role) + r":`~?)" + re.escape(broken_target) + r"(`)"
        )
        fixed_line = pattern.sub(r"\g<1>" + new_target + r"\g<2>", original_line)

        if fixed_line == original_line:
            # No replacement happened (target not found in line as expected)
            continue

        proposals.append(FixProposal(
            file_path=finding.file,
            line_number=finding.line,
            original_text=original_line,
            fixed_text=fixed_line,
            old_target=broken_target,
            new_target=new_target,
            category=finding.category,
            confidence=confidence,
            finding=finding,
        ))

    return proposals

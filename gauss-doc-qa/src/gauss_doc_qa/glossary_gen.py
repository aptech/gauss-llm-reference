"""Auto-generate a draft glossary YAML from corpus term frequency analysis.

Walks docutils AST nodes to extract terms from paragraph text (excluding
code blocks), groups case variants and plural/singular forms, and outputs
a YAML file compatible with load_glossary().
"""

from __future__ import annotations

import re
from collections import Counter

import yaml
from docutils import nodes

from gauss_doc_qa.models import ParsedDoc


# ---------------------------------------------------------------------------
# Stopwords: common English words and RST artifacts that should never be terms
# ---------------------------------------------------------------------------
_STOPWORDS: set[str] = {
    "The", "This", "That", "These", "Those",
    "When", "Where", "Which", "What",
    "From", "Into", "With", "About",
    "After", "Before", "Between", "During", "Since", "Through", "Until", "Upon",
    "Also", "Both", "Each", "Either", "Every",
    "However", "Neither", "Other", "Some", "Such",
    "Than", "Then", "There", "Here",
    "Most", "More", "Less", "Many", "Much",
    "None", "Only", "Same", "Very", "Just", "Even", "Still",
    "Note", "Example", "Following",
    "Parameters", "Returns", "See", "Type", "Format",
    "Purpose", "Remarks", "Source", "Description",
    "Default", "Global", "Input", "Output", "Syntax",
}
_STOPWORDS_LOWER: set[str] = {w.lower() for w in _STOPWORDS}

# Regex patterns
_MULTIWORD_RE = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Za-z]{3,}){1,2})\b')
_MULTIWORD_2_RE = re.compile(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b')
_PROPER_NOUN_RE = re.compile(r'\b([A-Z][a-z]{3,})\b')
_ALL_CAPS_RE = re.compile(r'\b([A-Z]{3,})\b')

# Simple plural -> singular mappings
_PLURAL_RULES: list[tuple[str, str]] = [
    ("ices", "ix"),    # matrices -> matrix
    ("ces", "x"),      # indices -> index (fallback)
    ("ies", "y"),      # series -> ... (skip if singular exists)
    ("ses", "s"),      # analyses -> analysis... tricky
    ("es", "e"),       # types -> type
    ("s", ""),         # functions -> function
]


def _ancestors(node: nodes.Node):
    """Yield ancestor nodes from parent to root."""
    current = node.parent
    while current is not None:
        yield current
        current = current.parent


def _is_inside_literal_block(node: nodes.Node) -> bool:
    """Check if a node is inside a literal_block (code example)."""
    return any(isinstance(p, nodes.literal_block) for p in _ancestors(node))


def _is_inside_system_message(node: nodes.Node) -> bool:
    """Check if a node is inside a system_message."""
    return any(isinstance(p, nodes.system_message) for p in _ancestors(node))


def _is_stopword(word: str) -> bool:
    """Check if a word is a stopword."""
    return word.lower() in _STOPWORDS_LOWER


def _singularize(word: str) -> str | None:
    """Attempt to produce a singular form. Returns None if no rule applies."""
    lower = word.lower()
    for suffix, replacement in _PLURAL_RULES:
        if lower.endswith(suffix) and len(lower) > len(suffix) + 2:
            return word[: len(word) - len(suffix)] + replacement
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_terms(parsed_docs: list[ParsedDoc]) -> Counter:
    """Extract term frequencies from parsed RST documents.

    Walks each ParsedDoc.raw_doc using docutils node traversal, collecting text
    from paragraph, title, and term nodes while skipping literal_block and
    system_message content.

    Returns a Counter mapping term -> total count across all documents.
    """
    counts: Counter = Counter()

    for pdoc in parsed_docs:
        doc = pdoc.raw_doc
        # Collect text from paragraph, title, and term nodes
        target_types = (nodes.paragraph, nodes.title, nodes.term)
        for node in doc.findall(lambda n: isinstance(n, target_types)):
            # Skip nodes inside literal_block or system_message
            if _is_inside_literal_block(node) or _is_inside_system_message(node):
                continue

            text = node.astext()

            # Extract multi-word terms (2-3 words starting with capital)
            for match in _MULTIWORD_RE.finditer(text):
                term = match.group(1)
                first_word = term.split()[0]
                if not _is_stopword(first_word):
                    counts[term] += 1

            # Also extract 2-word capitalized terms separately
            # (the 3-word regex may subsume them)
            for match in _MULTIWORD_2_RE.finditer(text):
                term = match.group(1)
                first_word = term.split()[0]
                if not _is_stopword(first_word):
                    counts[term] += 1

            # Extract single-word proper nouns (capitalized, >= 4 chars)
            for match in _PROPER_NOUN_RE.finditer(text):
                word = match.group(1)
                if not _is_stopword(word):
                    counts[word] += 1

            # Extract all-caps words (>= 3 chars, e.g., GAUSS, ARIMA)
            for match in _ALL_CAPS_RE.finditer(text):
                word = match.group(1)
                if not _is_stopword(word):
                    counts[word] += 1

    return counts


def group_terms(term_counts: Counter, min_freq: int = 3) -> list[dict]:
    """Group terms by case-insensitive form and plural/singular variants.

    Args:
        term_counts: Counter of term -> frequency from extract_terms().
        min_freq: Minimum total frequency for a group to be included.

    Returns:
        List of dicts with keys: canonical, aliases, category, count.
        Sorted by count descending.
    """
    # Step 1: Group by lowercase form
    case_groups: dict[str, Counter] = {}
    for term, count in term_counts.items():
        key = term.lower()
        if key not in case_groups:
            case_groups[key] = Counter()
        case_groups[key][term] = count

    # Step 2: Merge plural/singular groups
    merged: dict[str, Counter] = {}
    merged_keys: set[str] = set()

    for key in sorted(case_groups.keys()):
        if key in merged_keys:
            continue

        # Try to find a singular form
        singular = _singularize(key)
        if singular and singular.lower() in case_groups and singular.lower() != key:
            singular_key = singular.lower()
            if singular_key not in merged_keys:
                # Merge into singular group
                combined = Counter()
                combined.update(case_groups.get(singular_key, Counter()))
                combined.update(case_groups[key])
                merged[singular_key] = combined
                merged_keys.add(key)
                merged_keys.add(singular_key)
                continue

        if key not in merged_keys:
            merged[key] = case_groups[key]
            merged_keys.add(key)

    # Step 3: Build output groups
    groups: list[dict] = []
    for _key, variant_counts in merged.items():
        total = sum(variant_counts.values())
        if total < min_freq:
            continue

        # Most frequent variant is canonical
        canonical = variant_counts.most_common(1)[0][0]
        aliases = sorted(
            [v for v in variant_counts if v != canonical],
            key=str,
        )

        # Skip terms with no aliases (single variant only)
        # Actually, keep them -- they're still valid glossary terms
        groups.append({
            "canonical": canonical,
            "aliases": aliases if aliases else [canonical.lower()] if canonical.lower() != canonical else [canonical.upper()],
            "category": "auto-detected",
            "count": total,
        })

    # Sort by count descending
    groups.sort(key=lambda g: g["count"], reverse=True)
    return groups


def generate_glossary_yaml(groups: list[dict]) -> str:
    """Generate a YAML string compatible with load_glossary().

    Args:
        groups: List of dicts from group_terms() with canonical, aliases,
                category, and count keys.

    Returns:
        YAML string with comment header and glossary: top-level key.
    """
    # Build entries without the 'count' field
    entries = []
    for g in groups:
        entry = {
            "canonical": g["canonical"],
            "aliases": g["aliases"],
            "category": g["category"],
            "description": "",
        }
        entries.append(entry)

    data = {"glossary": entries}
    yaml_body = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return f"# Draft glossary — auto-generated. Review and curate before use.\n{yaml_body}"

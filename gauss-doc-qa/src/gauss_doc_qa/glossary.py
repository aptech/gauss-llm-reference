"""Glossary data model and YAML loader for terminology enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field

import yaml


@dataclass
class GlossaryEntry:
    """A single glossary term with its canonical form and known aliases."""

    canonical: str  # The preferred term (e.g., "GAUSS")
    aliases: list[str]  # Non-canonical variants to flag (e.g., ["Gauss", "gauss"])
    category: str  # Grouping (e.g., "product", "concept", "function")
    description: str = ""  # Optional explanation of the term


def load_glossary(path: str) -> list[GlossaryEntry]:
    """Load a YAML glossary file and return validated GlossaryEntry list.

    Expected YAML schema::

        glossary:
          - canonical: "GAUSS"
            aliases: ["Gauss", "gauss"]
            category: "product"
            description: "Always uppercase when referring to the software"

    Raises:
        ValueError: If any entry is missing required fields or has wrong types.
        FileNotFoundError: If the YAML file does not exist.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "glossary" not in data:
        raise ValueError(
            f"Glossary YAML must have a top-level 'glossary' key; got: {type(data)}"
        )

    raw_entries = data["glossary"]
    if not isinstance(raw_entries, list):
        raise ValueError(
            f"'glossary' must be a list of entries; got: {type(raw_entries)}"
        )

    entries: list[GlossaryEntry] = []
    for i, raw in enumerate(raw_entries):
        if not isinstance(raw, dict):
            raise ValueError(f"Glossary entry {i} must be a mapping; got: {type(raw)}")

        # Validate canonical
        canonical = raw.get("canonical")
        if not canonical or not isinstance(canonical, str):
            raise ValueError(
                f"Glossary entry {i}: 'canonical' must be a non-empty string"
            )

        # Validate aliases
        aliases = raw.get("aliases")
        if aliases is None:
            raise ValueError(f"Glossary entry {i} ('{canonical}'): 'aliases' is required")
        if not isinstance(aliases, list) or len(aliases) == 0:
            raise ValueError(
                f"Glossary entry {i} ('{canonical}'): 'aliases' must be a non-empty list"
            )
        for j, alias in enumerate(aliases):
            if not isinstance(alias, str) or not alias.strip():
                raise ValueError(
                    f"Glossary entry {i} ('{canonical}'): alias {j} must be a non-empty string"
                )

        # Validate category
        category = raw.get("category", "")
        if not isinstance(category, str):
            raise ValueError(
                f"Glossary entry {i} ('{canonical}'): 'category' must be a string"
            )

        description = raw.get("description", "")
        if not isinstance(description, str):
            description = str(description)

        entries.append(
            GlossaryEntry(
                canonical=canonical,
                aliases=aliases,
                category=category,
                description=description,
            )
        )

    return entries


def build_alias_map(entries: list[GlossaryEntry]) -> dict[str, GlossaryEntry]:
    """Build a lookup dict mapping each lowercase alias to its GlossaryEntry.

    Raises:
        ValueError: If two entries share the same alias (case-insensitive).
    """
    alias_map: dict[str, GlossaryEntry] = {}
    for entry in entries:
        for alias in entry.aliases:
            key = alias.lower()
            if key in alias_map:
                existing = alias_map[key]
                raise ValueError(
                    f"Alias conflict: '{alias}' (lowercased: '{key}') is claimed by "
                    f"both '{existing.canonical}' and '{entry.canonical}'"
                )
            alias_map[key] = entry
    return alias_map

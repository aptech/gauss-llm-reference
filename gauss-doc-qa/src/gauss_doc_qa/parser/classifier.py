import os
from pathlib import PurePosixPath

from gauss_doc_qa.models import DocType


# Known operator page stems
_OPERATOR_STEMS = frozenset({
    "addition",
    "subtraction",
    "multiplication",
    "division",
    "assignment",
    "hat",
    "dot-operators",
    "kron",
    "mod-operator",
    "exponent",
})

# Known app module directory names
_APP_MODULE_DIRS = frozenset({
    "ad",
    "bet",
    "bhatlib",
    "cc",
    "cf",
    "cmlmt",
    "comt",
    "dc",
    "ds",
    "fanpac",
    "llmt",
    "lpmt",
    "lrmt",
    "maxlikmt",
    "mlmt",
    "optmt",
    "sslib",
    "tsmt",
})

# Subdirectory -> DocType mapping
_SUBDIR_MAP = {
    "getting-started": DocType.GETTING_STARTED,
    "user-guide": DocType.USER_GUIDE,
    "graphics-guide": DocType.GRAPHICS_GUIDE,
    "coming-to-gauss": DocType.USER_GUIDE,
    "data-management": DocType.USER_GUIDE,
    "textbook-examples": DocType.USER_GUIDE,
    "plot-gallery": DocType.GRAPHICS_GUIDE,
}

# Top-level non-function files (overview, index, etc.)
_NON_FUNCTION_STEMS = frozenset({
    "index",
    "applications",
    "command-reference",
    "changelog",
    "schtoc",
    "data-management",
    "learning-resources",
    "gml-landing",
    "machine-learning",
})


def classify_doc(filepath: str, base_dir: str) -> DocType:
    """Classify an RST file into a DocType based on its path relative to base_dir.

    Classification rules (in priority order):
    1. Path contains /include/ segment -> INCLUDE_FRAGMENT
    2. Subdirectory mapping (getting-started, user-guide, graphics-guide) -> mapped type
    3. Known app module dirs -> APP_MODULE
    4. Top-level file, stem is single letter (a-z) or underscore -> ALPHA_INDEX
    5. Top-level file, stem in known operator set -> OPERATOR
    6. Default -> COMMAND_REF
    """
    # Normalize paths
    filepath = filepath.replace(os.sep, "/")
    base_dir = base_dir.rstrip("/").replace(os.sep, "/")

    # Get relative path
    if filepath.startswith(base_dir + "/"):
        rel_path = filepath[len(base_dir) + 1:]
    else:
        rel_path = filepath

    parts = PurePosixPath(rel_path).parts

    # Rule 1: include/ segment
    if "include" in parts[:-1]:  # check directory parts, not the filename
        return DocType.INCLUDE_FRAGMENT

    # Rule 2 & 3: Check subdirectory names
    for part in parts[:-1]:
        if part in _SUBDIR_MAP:
            return _SUBDIR_MAP[part]
        if part in _APP_MODULE_DIRS:
            return DocType.APP_MODULE

    # Rule 4: index.rst in any directory -> ALPHA_INDEX
    stem = PurePosixPath(parts[-1]).stem
    if stem == "index":
        return DocType.ALPHA_INDEX

    # Rules 5-7: Top-level files only (no subdirectory)
    if len(parts) == 1:
        # Rule 5: Single letter or underscore -> ALPHA_INDEX
        if len(stem) == 1 and (stem.isalpha() or stem == "_"):
            return DocType.ALPHA_INDEX

        # Rule 6: Known non-function files -> ALPHA_INDEX
        if stem in _NON_FUNCTION_STEMS:
            return DocType.ALPHA_INDEX

        # Rule 7: Known operator
        if stem in _OPERATOR_STEMS:
            return DocType.OPERATOR

    # Rule 8: Files in unmapped subdirectories with "-examples" or "-ug-" in name -> guide
    if len(parts) > 1 and ("-examples" in stem or "-ug-" in stem):
        return DocType.USER_GUIDE

    # Rule 9: Default
    return DocType.COMMAND_REF

"""Tests for glossary model, YAML loader, and GlossaryChecker."""

import pytest

from gauss_doc_qa.glossary import GlossaryEntry, build_alias_map, load_glossary
from gauss_doc_qa.checkers.glossary import GlossaryChecker
from gauss_doc_qa.models import DocType, ParsedDoc, Severity


# ---------------------------------------------------------------------------
# Helper: minimal ParsedDoc pointing at a real file on disk
# ---------------------------------------------------------------------------

def _make_parsed_doc(path: str) -> ParsedDoc:
    """Create a minimal ParsedDoc whose .path points to a real RST file."""
    return ParsedDoc(
        path=path,
        doc_type=DocType.COMMAND_REF,
        title="test",
        sections=[],
        code_blocks=[],
        field_lists=[],
        raw_doc=None,
    )


# ---------------------------------------------------------------------------
# Sample YAML content
# ---------------------------------------------------------------------------

VALID_YAML = """\
glossary:
  - canonical: "GAUSS"
    aliases: ["Gauss", "gauss"]
    category: "product"
    description: "Always uppercase"
  - canonical: "dataframe"
    aliases: ["data frame", "DataFrame", "data-frame"]
    category: "concept"
"""


# ===========================================================================
# Glossary loading tests
# ===========================================================================


class TestLoadGlossary:

    def test_load_glossary_valid(self, tmp_path):
        p = tmp_path / "glossary.yaml"
        p.write_text(VALID_YAML)
        entries = load_glossary(str(p))
        assert len(entries) == 2
        assert entries[0].canonical == "GAUSS"
        assert entries[0].aliases == ["Gauss", "gauss"]
        assert entries[0].category == "product"
        assert entries[0].description == "Always uppercase"
        assert entries[1].canonical == "dataframe"
        assert entries[1].aliases == ["data frame", "DataFrame", "data-frame"]

    def test_load_glossary_missing_canonical(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("glossary:\n  - aliases: ['x']\n    category: 'a'\n")
        with pytest.raises(ValueError, match="canonical"):
            load_glossary(str(p))

    def test_load_glossary_empty_aliases(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("glossary:\n  - canonical: 'X'\n    aliases: []\n    category: 'a'\n")
        with pytest.raises(ValueError, match="aliases"):
            load_glossary(str(p))

    def test_load_glossary_missing_aliases(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("glossary:\n  - canonical: 'X'\n    category: 'a'\n")
        with pytest.raises(ValueError, match="aliases"):
            load_glossary(str(p))

    def test_load_glossary_no_glossary_key(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("terms:\n  - canonical: 'X'\n")
        with pytest.raises(ValueError, match="glossary"):
            load_glossary(str(p))

    def test_load_glossary_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_glossary("/nonexistent/path.yaml")


# ===========================================================================
# Alias map tests
# ===========================================================================


class TestBuildAliasMap:

    def test_build_alias_map(self):
        entries = [
            GlossaryEntry("GAUSS", ["Gauss", "gauss"], "product"),
            GlossaryEntry("dataframe", ["data frame"], "concept"),
        ]
        amap = build_alias_map(entries)
        assert "gauss" in amap
        assert amap["gauss"].canonical == "GAUSS"
        assert "data frame" in amap
        assert amap["data frame"].canonical == "dataframe"

    def test_build_alias_map_conflict(self):
        entries = [
            GlossaryEntry("GAUSS", ["gauss"], "product"),
            GlossaryEntry("Gauss Math", ["gauss"], "concept"),
        ]
        with pytest.raises(ValueError, match="conflict"):
            build_alias_map(entries)


# ===========================================================================
# Checker tests
# ===========================================================================


class TestGlossaryChecker:

    @pytest.fixture
    def entries(self):
        return [
            GlossaryEntry("GAUSS", ["Gauss", "gauss"], "product", "Always uppercase"),
            GlossaryEntry("dataframe", ["data frame", "DataFrame", "data-frame"], "concept"),
        ]

    @pytest.fixture
    def checker(self, entries):
        return GlossaryChecker(entries)

    def test_flags_alias(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nThis uses Gauss for analysis.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 1
        assert findings[0].severity == Severity.WARNING
        assert findings[0].category == "terminology"
        assert findings[0].checker == "glossary"
        assert "Use 'GAUSS' instead" in findings[0].message
        assert "'Gauss'" in findings[0].message
        assert findings[0].line == 4

    def test_canonical_no_finding(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nThis uses GAUSS for analysis.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_case_insensitive(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nThe gauss software is great.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 1
        assert "Use 'GAUSS' instead" in findings[0].message

    def test_skips_code_blocks(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text(
            "Title\n=====\n\n"
            ".. code-block:: gauss\n\n"
            "   x = Gauss_function();\n\n"
            "Back to normal text with GAUSS here.\n"
        )
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        # Only canonical "GAUSS" in normal text -- should be zero findings
        assert len(findings) == 0

    def test_multiple_aliases(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text(
            "Title\n=====\n\n"
            "Use Gauss for analysis.\n\n"
            "Create a data frame here.\n"
        )
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 2
        # Verify correct line numbers
        lines = {f.line for f in findings}
        assert 4 in lines
        assert 6 in lines

    def test_word_boundary(self, tmp_path):
        """'Gaussian' should NOT be flagged when 'Gauss' is an alias."""
        entries = [GlossaryEntry("GAUSS", ["Gauss"], "product")]
        checker = GlossaryChecker(entries)
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nGaussian distribution is normal.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_skips_literal_block(self, checker, tmp_path):
        """Lines under :: literal blocks should be skipped."""
        rst = tmp_path / "test.rst"
        rst.write_text(
            "Title\n=====\n\n"
            "Example::\n\n"
            "   Gauss code here\n\n"
            "Normal text with GAUSS.\n"
        )
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_multi_word_alias(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nUse a data frame for storage.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 1
        assert "Use 'dataframe' instead" in findings[0].message

    def test_dataframe_alias(self, checker, tmp_path):
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nCreate a DataFrame object.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 1
        assert "Use 'dataframe' instead" in findings[0].message

    def test_file_not_found_returns_empty(self, checker):
        doc = _make_parsed_doc("/nonexistent/file.rst")
        findings = checker.check(doc)
        assert len(findings) == 0

    def test_empty_entries(self, tmp_path):
        """Checker with no entries produces no findings."""
        checker = GlossaryChecker([])
        rst = tmp_path / "test.rst"
        rst.write_text("Title\n=====\n\nAnything here.\n")
        doc = _make_parsed_doc(str(rst))
        findings = checker.check(doc)
        assert len(findings) == 0

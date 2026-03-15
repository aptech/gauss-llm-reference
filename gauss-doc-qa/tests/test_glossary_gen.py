"""Tests for glossary generation from corpus term frequency analysis."""

import tempfile
from collections import Counter
from pathlib import Path

import pytest
from docutils.utils import new_document
from docutils.parsers.rst import Parser
from docutils.frontend import OptionParser

from gauss_doc_qa.models import ParsedDoc, DocType
from gauss_doc_qa.glossary_gen import extract_terms, group_terms, generate_glossary_yaml


def _make_parsed_doc(rst_content: str, path: str = "test.rst") -> ParsedDoc:
    """Helper: parse RST string into a ParsedDoc."""
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    settings.report_level = 5
    settings.halt_level = 5
    doc = new_document(path, settings)
    parser.parse(rst_content, doc)
    return ParsedDoc(
        path=path,
        doc_type=DocType.OTHER,
        title="Test",
        sections=[],
        code_blocks=[],
        field_lists=[],
        raw_doc=doc,
    )


class TestExtractTerms:
    def test_extract_terms_from_paragraphs(self):
        """Terms from paragraph text are counted."""
        rst = (
            "Title\n=====\n\n"
            "GAUSS is a matrix language. GAUSS supports many features.\n"
            "GAUSS is used for econometrics.\n"
        )
        parsed = _make_parsed_doc(rst)
        counts = extract_terms([parsed])
        assert counts["GAUSS"] >= 3

    def test_extract_terms_skips_code_blocks(self):
        """Code block content should NOT contribute terms."""
        rst = (
            "Title\n=====\n\n"
            "Some text here.\n\n"
            "::\n\n"
            "   CodeVariable = something;\n"
            "   AnotherThing = 42;\n"
        )
        parsed = _make_parsed_doc(rst)
        counts = extract_terms([parsed])
        # CodeVariable and AnotherThing should not appear
        assert "CodeVariable" not in counts
        assert "AnotherThing" not in counts

    def test_extract_terms_captures_multiword(self):
        """Multi-word terms like 'Time Series' should be captured."""
        rst = (
            "Title\n=====\n\n"
            + "Time Series analysis is important. "
            * 5
        )
        parsed = _make_parsed_doc(rst)
        counts = extract_terms([parsed])
        assert "Time Series" in counts
        assert counts["Time Series"] >= 5

    def test_extract_terms_excludes_stopwords(self):
        """Stopwords like 'The', 'This', 'Note' should be excluded."""
        rst = (
            "Title\n=====\n\n"
            "Note that this is important. "
            "Note the following parameters.\n"
            "Note the example below.\n"
        )
        parsed = _make_parsed_doc(rst)
        counts = extract_terms([parsed])
        assert "Note" not in counts


class TestGroupTerms:
    def test_group_terms_case_variants(self):
        """Case variants are grouped; most frequent becomes canonical."""
        counts = Counter({"GAUSS": 10, "Gauss": 5, "gauss": 2})
        groups = group_terms(counts, min_freq=1)
        assert len(groups) == 1
        assert groups[0]["canonical"] == "GAUSS"
        assert sorted(groups[0]["aliases"]) == ["Gauss", "gauss"]

    def test_group_terms_min_freq(self):
        """Terms below min_freq are filtered out."""
        counts = Counter({"GAUSS": 10, "Rare": 1, "Also Rare": 2})
        groups = group_terms(counts, min_freq=3)
        canonicals = [g["canonical"] for g in groups]
        assert "GAUSS" in canonicals
        assert "Rare" not in canonicals
        assert "Also Rare" not in canonicals

    def test_group_terms_plural_singular(self):
        """Plural/singular variants are grouped; singular is preferred."""
        counts = Counter({"matrices": 5, "matrix": 10})
        groups = group_terms(counts, min_freq=1)
        assert len(groups) == 1
        assert groups[0]["canonical"] == "matrix"
        assert "matrices" in groups[0]["aliases"]

    def test_group_terms_sorted_by_count(self):
        """Output should be sorted by total count descending."""
        counts = Counter({"Alpha": 5, "Beta": 20, "Gamma": 10})
        groups = group_terms(counts, min_freq=1)
        assert groups[0]["canonical"] == "Beta"
        assert groups[1]["canonical"] == "Gamma"
        assert groups[2]["canonical"] == "Alpha"


class TestGenerateGlossaryYaml:
    def test_generate_glossary_yaml_roundtrip(self, tmp_path):
        """Generated YAML can be loaded by load_glossary() without error."""
        from gauss_doc_qa.glossary import load_glossary

        groups = [
            {"canonical": "GAUSS", "aliases": ["Gauss", "gauss"], "category": "auto-detected", "count": 17},
            {"canonical": "Time Series", "aliases": ["time series"], "category": "auto-detected", "count": 8},
        ]
        yaml_output = generate_glossary_yaml(groups)

        out_file = tmp_path / "glossary.yaml"
        out_file.write_text(yaml_output)
        entries = load_glossary(str(out_file))
        assert len(entries) == 2
        assert entries[0].canonical == "GAUSS"
        assert "Gauss" in entries[0].aliases

    def test_generate_glossary_yaml_format(self):
        """Output has the comment header and glossary: key."""
        groups = [
            {"canonical": "Test", "aliases": ["test"], "category": "auto-detected", "count": 5},
        ]
        yaml_output = generate_glossary_yaml(groups)
        assert yaml_output.startswith("# Draft glossary")
        assert "glossary:" in yaml_output

    def test_generate_glossary_yaml_no_count_field(self):
        """The 'count' field used for sorting should NOT appear in YAML output."""
        groups = [
            {"canonical": "Test", "aliases": ["test"], "category": "auto-detected", "count": 5},
        ]
        yaml_output = generate_glossary_yaml(groups)
        assert "count:" not in yaml_output
        assert "count" not in yaml_output.split("glossary:")[1]

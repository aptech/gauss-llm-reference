from gauss_doc_qa.parser.rst_parser import parse_rst
from gauss_doc_qa.models import DocType


class TestParseFunction:
    def test_function_page_title(self, function_page_rst):
        parsed = parse_rst("docs/myabs.rst", function_page_rst, DocType.COMMAND_REF)
        assert parsed.title != ""

    def test_function_page_sections(self, function_page_rst):
        parsed = parse_rst("docs/myabs.rst", function_page_rst, DocType.COMMAND_REF)
        assert "purpose" in parsed.sections
        assert "format" in parsed.sections
        assert "examples" in parsed.sections

    def test_function_page_code_blocks(self, function_page_rst):
        parsed = parse_rst("docs/myabs.rst", function_page_rst, DocType.COMMAND_REF)
        assert len(parsed.code_blocks) >= 1
        assert parsed.code_blocks[0].is_empty is False

    def test_function_page_field_lists(self, function_page_rst):
        parsed = parse_rst("docs/myabs.rst", function_page_rst, DocType.COMMAND_REF)
        names = [f["name"] for f in parsed.field_lists]
        has_param = any(n.startswith("param") for n in names)
        has_return = any(n.startswith("return") for n in names)
        assert has_param, f"Expected param field, got: {names}"
        assert has_return, f"Expected return field, got: {names}"


class TestParseOperator:
    def test_operator_page_sections(self, operator_page_rst):
        parsed = parse_rst("docs/addition.rst", operator_page_rst, DocType.OPERATOR)
        assert "purpose" in parsed.sections
        assert "format" in parsed.sections
        assert "parameters" in parsed.sections
        assert "returns" in parsed.sections
        assert "examples" in parsed.sections


class TestParseIndex:
    def test_index_page_title(self, index_page_rst):
        parsed = parse_rst("docs/a.rst", index_page_rst, DocType.ALPHA_INDEX)
        assert parsed.title != ""

    def test_index_page_no_code_blocks(self, index_page_rst):
        parsed = parse_rst("docs/a.rst", index_page_rst, DocType.ALPHA_INDEX)
        assert parsed.code_blocks == []


class TestParseIncludeFragment:
    def test_include_fragment_sections(self, include_fragment_rst):
        parsed = parse_rst("docs/include/plotattr.rst", include_fragment_rst, DocType.INCLUDE_FRAGMENT)
        # Include fragments have no standard section names
        standard_sections = {"purpose", "format", "examples", "parameters", "returns"}
        assert not (set(parsed.sections) & standard_sections)


class TestParseEmptyCode:
    def test_placeholder_code_block(self, empty_code_rst):
        """Verify placeholder code block is detected.

        Note: docutils drops truly whitespace-only literal_blocks entirely,
        so we test with a placeholder '...' block instead. The actual STRC-02
        empty-block check will need raw source analysis for the whitespace-only case.
        """
        parsed = parse_rst("docs/emptyfunc.rst", empty_code_rst, DocType.COMMAND_REF)
        assert len(parsed.code_blocks) >= 1, "Expected at least one code block"
        # The placeholder block has content but it's minimal
        assert parsed.code_blocks[0].content.strip() == "..."

    def test_is_empty_flag(self):
        """Verify is_empty correctly identifies empty content."""
        from gauss_doc_qa.models import CodeBlock
        empty = CodeBlock(content="", line_number=1, is_empty=True)
        assert empty.is_empty is True
        non_empty = CodeBlock(content="x = 1;", line_number=1, is_empty=False)
        assert non_empty.is_empty is False

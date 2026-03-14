import re

from docutils.utils import new_document
from docutils.parsers.rst import Parser
from docutils.frontend import OptionParser
from docutils import nodes

from gauss_doc_qa.models import ParsedDoc, CodeBlock, DocType


def parse_rst(filepath: str, content: str, doc_type: DocType = DocType.OTHER) -> ParsedDoc:
    """Parse RST content into a ParsedDoc using docutils AST."""
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    settings.report_level = 5  # SEVERE only -- suppress unknown directive warnings
    settings.halt_level = 5
    doc = new_document(filepath, settings)
    parser.parse(content, doc)

    title = _extract_title(doc)
    sections = _extract_sections(doc)
    code_blocks = _extract_code_blocks(doc)
    field_lists = _extract_field_lists(doc)

    return ParsedDoc(
        path=filepath,
        doc_type=doc_type,
        title=title,
        sections=sections,
        code_blocks=code_blocks,
        field_lists=field_lists,
        raw_doc=doc,
    )


def _extract_title(doc: nodes.document) -> str:
    """Get the first section's title text."""
    for section in doc.findall(nodes.section):
        if section.children and isinstance(section.children[0], nodes.title):
            return section.children[0].astext().strip()
    return ""


def _extract_sections(doc: nodes.document) -> list[str]:
    """Extract all section titles, normalized to lowercase stripped."""
    sections = []
    for section in doc.findall(nodes.section):
        if section.children and isinstance(section.children[0], nodes.title):
            sections.append(section.children[0].astext().strip().lower())
    return sections


def _extract_code_blocks(doc: nodes.document) -> list[CodeBlock]:
    """Extract all literal_block nodes as CodeBlock objects.

    Note: literal_block nodes inside system_message nodes (from unrecognized
    directives like ``.. function::``) are excluded -- they contain directive
    source text, not actual code examples.
    """
    blocks = []
    for node in doc.findall(nodes.literal_block):
        # Skip literal_blocks inside system_message nodes -- these contain
        # unrecognized directive source text (e.g., ``.. function::``), not
        # actual code examples.
        if any(isinstance(p, nodes.system_message) for p in _ancestors(node)):
            continue
        content = node.astext()
        blocks.append(CodeBlock(
            content=content,
            line_number=node.line,
            is_empty=not content.strip(),
        ))
    return blocks


def _ancestors(node: nodes.Node):
    """Yield ancestor nodes from parent to root."""
    current = node.parent
    while current is not None:
        yield current
        current = current.parent


def _extract_field_lists(doc: nodes.document) -> list[dict]:
    """Extract field list entries as list of {name, body} dicts.

    Handles two cases:
    1. Standard field_list nodes (from operator pages with bare field lists)
    2. Pseudo-fields inside system_message literal_blocks (from unrecognized
       ``.. function::`` directives, which docutils cannot parse as Sphinx
       directives)
    """
    fields = []

    # Case 1: Standard field_list nodes
    for field_list in doc.findall(nodes.field_list):
        for field in field_list.findall(nodes.field):
            children = list(field.children)
            if len(children) >= 2:
                field_name = children[0].astext()
                field_body = children[1].astext()
                fields.append({"name": field_name, "body": field_body})

    # Case 2: Extract from system_message literal blocks
    # When docutils encounters ``.. function::`` (a Sphinx directive),
    # it creates a system_message with the directive content as a literal_block.
    # We parse :param:, :type:, :return:, :rtype: entries from that text.
    _FIELD_RE = re.compile(r":(\w+(?:\s+\w+)?)\s*:\s*(.*)")
    for sys_msg in doc.findall(nodes.system_message):
        for lb in sys_msg.findall(nodes.literal_block):
            text = lb.astext()
            if ".. function::" in text or ":param" in text or ":return" in text:
                for match in _FIELD_RE.finditer(text):
                    fields.append({"name": match.group(1), "body": match.group(2).strip()})

    return fields

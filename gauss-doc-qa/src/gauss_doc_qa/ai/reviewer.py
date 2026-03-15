"""Core review engine: submits docs to Claude API and converts results to Findings."""

from __future__ import annotations

from docutils import nodes

from gauss_doc_qa.models import Finding, ParsedDoc
from gauss_doc_qa.ai.personas import Persona
from gauss_doc_qa.ai.schemas import PersonaReviewResponse, CheckResult


def extract_doc_text(parsed_doc: ParsedDoc, persona: Persona) -> str:
    """Extract text content from ParsedDoc's raw_doc (docutils document).

    Walks the docutils tree and extracts text from paragraph, literal_block,
    and title nodes. Strips RST directive syntax. Returns plain text with
    section headings preserved.

    For expert persona on COMMAND_REF pages: focuses on extracting Format,
    Examples, and Parameters sections if present.
    For newcomer/writer: extracts full page content.
    """
    doc = parsed_doc.raw_doc
    if not isinstance(doc, nodes.document):
        return ""

    if persona.name == "expert":
        return _extract_expert_sections(doc)
    return _extract_full_text(doc)


def _extract_full_text(doc: nodes.document) -> str:
    """Extract all text content from the document."""
    parts: list[str] = []
    for node in doc.findall():
        if isinstance(node, nodes.title):
            parts.append(f"\n## {node.astext()}\n")
        elif isinstance(node, nodes.paragraph):
            text = node.astext().strip()
            if text:
                parts.append(text)
        elif isinstance(node, nodes.literal_block):
            # Skip literal blocks inside system_message (directive source)
            if any(isinstance(p, nodes.system_message) for p in _ancestors(node)):
                continue
            parts.append(f"\n```\n{node.astext()}\n```\n")
    return "\n".join(parts)


def _extract_expert_sections(doc: nodes.document) -> str:
    """Extract Format, Examples, and Parameters sections for expert review."""
    target_sections = {"format", "examples", "parameters", "returns", "purpose"}
    parts: list[str] = []
    in_target = False

    for node in doc.findall():
        if isinstance(node, nodes.section):
            title_node = node.children[0] if node.children else None
            if isinstance(title_node, nodes.title):
                section_name = title_node.astext().strip().lower()
                in_target = section_name in target_sections
                if in_target:
                    parts.append(f"\n## {title_node.astext()}\n")
        elif in_target:
            if isinstance(node, nodes.paragraph):
                text = node.astext().strip()
                if text:
                    parts.append(text)
            elif isinstance(node, nodes.literal_block):
                if not any(isinstance(p, nodes.system_message) for p in _ancestors(node)):
                    parts.append(f"\n```\n{node.astext()}\n```\n")

    # Also extract the function directive info from system_message blocks
    for sys_msg in doc.findall(nodes.system_message):
        for lb in sys_msg.findall(nodes.literal_block):
            text = lb.astext()
            if ".. function::" in text:
                parts.insert(0, f"Function directive:\n{text}\n")

    if not parts:
        # Fallback: extract full text if no target sections found
        return _extract_full_text(doc)

    return "\n".join(parts)


def _ancestors(node: nodes.Node):
    """Yield ancestor nodes from parent to root."""
    current = node.parent
    while current is not None:
        yield current
        current = current.parent


def build_rubric_prompt(persona: Persona) -> str:
    """Format the rubric checks into a numbered list for the system prompt."""
    lines = [
        "Evaluate the document against each check below.",
        "For each check, determine pass or fail.",
        "If fail, quote the specific evidence from the document.",
        "If pass, leave evidence empty.",
        "",
    ]
    for check in persona.rubric:
        lines.append(f"{check.id}: {check.question}")
    return "\n".join(lines)


def run_persona_review(parsed_doc: ParsedDoc, persona: Persona) -> list[Finding]:
    """Run a persona review on a parsed document via the Claude API.

    Extracts doc text, builds the system prompt with rubric, calls the
    Claude API with structured output, and converts the response to Findings.
    """
    doc_text = extract_doc_text(parsed_doc, persona)
    system_prompt = persona.description + "\n\n" + build_rubric_prompt(persona)

    # Lazy import to prevent CLI breakage when ANTHROPIC_API_KEY is not set
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=persona.model,
        max_tokens=1024,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Document ({parsed_doc.path}):\n\n{doc_text}",
            }
        ],
        output_format=PersonaReviewResponse,
    )

    review = response.parsed_output
    return review_to_findings(review, persona, parsed_doc.path)


def review_to_findings(
    review: PersonaReviewResponse,
    persona: Persona,
    file_path: str,
) -> list[Finding]:
    """Convert a PersonaReviewResponse into a list of Finding objects.

    Only failed checks produce Findings. Severity comes from the rubric
    config, not from Claude's output.
    """
    rubric_map = {r.id: r for r in persona.rubric}
    findings: list[Finding] = []

    for result in review.results:
        if not result.passed:
            check = rubric_map.get(result.check_id)
            if check is None:
                continue
            findings.append(
                Finding(
                    file=file_path,
                    line=None,
                    severity=check.fail_severity,
                    category=check.category,
                    checker=f"ai_{persona.name}",
                    message=f"[{result.check_id}] {check.question} -- {result.evidence}",
                    auto_fixable=False,
                )
            )

    return findings

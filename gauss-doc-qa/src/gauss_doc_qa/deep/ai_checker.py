"""AI-assisted example code verification for deep validation.

Uses the Claude API to check whether example code in function pages
contains real issues (wrong function calls, impossible params, etc.).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from gauss_doc_qa.deep.models import DeepCheckResult, DeepCheckType, DeepFunctionResult
from gauss_doc_qa.models import DocType, ParsedDoc
from gauss_doc_qa.parser.rst_parser import parse_rst


class ExampleCheckResult(BaseModel):
    """Structured response from Claude for example code verification."""

    has_issues: bool
    issues: list[str]  # Each issue is a one-line description


_SYSTEM_PROMPT_TEMPLATE = """\
You are a GAUSS programming language expert reviewing documentation examples.
Check the example code for the function '{function_name}'.

Flag issues ONLY if you are confident they are real problems:
1. Example calls a different function than the one being documented
2. Parameters that are clearly wrong (wrong type, impossible values)
3. Comments that contradict what the code does
4. Code that would produce an error in GAUSS

Do NOT flag:
- Style preferences
- Missing error handling
- Simplistic examples (that's OK for documentation)
"""


def ai_check_examples(parsed_doc: ParsedDoc, function_name: str) -> DeepCheckResult:
    """Use Claude API to verify example code correctness for a function page.

    Args:
        parsed_doc: Parsed RST document containing code blocks.
        function_name: Name of the function being documented.

    Returns:
        DeepCheckResult with AI_EXAMPLE_QUALITY check type.
    """
    # Extract non-empty code blocks
    code_blocks = [
        cb for cb in parsed_doc.code_blocks
        if not cb.is_empty and cb.content.strip()
    ]

    if not code_blocks:
        return DeepCheckResult(
            check=DeepCheckType.AI_EXAMPLE_QUALITY,
            passed=True,
            detail="No examples to verify",
        )

    # Build prompt content from code blocks
    code_text = "\n\n".join(
        f"```\n{cb.content}\n```" for cb in code_blocks
    )

    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(function_name=function_name)

    # Lazy import to prevent CLI breakage when ANTHROPIC_API_KEY is not set
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Review these example code blocks for the function '{function_name}':\n\n{code_text}",
            }
        ],
        output_format=ExampleCheckResult,
    )

    result = response.parsed_output

    if result.has_issues:
        return DeepCheckResult(
            check=DeepCheckType.AI_EXAMPLE_QUALITY,
            passed=False,
            detail="; ".join(result.issues),
        )
    else:
        return DeepCheckResult(
            check=DeepCheckType.AI_EXAMPLE_QUALITY,
            passed=True,
            detail="No issues found",
        )


def ai_check_examples_batch(
    results: list[DeepFunctionResult],
    docs_dir: str,
) -> list[DeepFunctionResult]:
    """Run AI example verification on a batch of deep validation results.

    Takes the structural check results from deep_check_functions(), reads
    each function's RST file, runs ai_check_examples(), and appends the
    AI check result to each function's checks list.

    Args:
        results: List of DeepFunctionResult from structural checks.
        docs_dir: Root directory of RST documentation.

    Returns:
        The updated list with AI check results appended.
    """
    docs_path = Path(docs_dir)

    for func_result in results:
        rst_file = Path(func_result.file_path)
        if not rst_file.exists():
            # If file doesn't exist, skip AI check for this function
            ai_result = DeepCheckResult(
                check=DeepCheckType.AI_EXAMPLE_QUALITY,
                passed=True,
                detail="RST file not found, skipping AI check",
            )
        else:
            content = rst_file.read_text(encoding="utf-8")
            parsed = parse_rst(str(rst_file), content, DocType.COMMAND_REF)
            ai_result = ai_check_examples(parsed, func_result.function_name)

        func_result.checks.append(ai_result)
        # Update overall_pass to include AI check
        func_result.overall_pass = all(c.passed for c in func_result.checks)

    return results

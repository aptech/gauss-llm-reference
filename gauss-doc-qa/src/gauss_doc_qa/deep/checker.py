"""Deep structural checker for per-function validation.

Runs 4 structural checks on each function page:
1. SIGNATURE_COMPLETE - all params documented
2. EXAMPLES_NONTRIVIAL - substantive code examples
3. RETURN_TYPE_DOCUMENTED - has :return: or :rtype: fields
4. SEEALSO_PRESENT - has .. seealso:: directive
"""

from __future__ import annotations

import re
from pathlib import Path

from docutils import nodes

from gauss_doc_qa.deep.models import DeepCheckResult, DeepCheckType, DeepFunctionResult
from gauss_doc_qa.models import DocType, ParsedDoc
from gauss_doc_qa.parser.rst_parser import parse_rst


# Reuse seealso pattern from checkers/seealso.py
SEEALSO_RE = re.compile(
    r"^\.\.\s+seealso::",
    re.MULTILINE,
)


def deep_check_function(parsed_doc: ParsedDoc) -> list[DeepCheckResult]:
    """Run all 4 deep checks on a single parsed function page.

    Returns a list of DeepCheckResult, one per check type.
    """
    return [
        _check_signature_complete(parsed_doc),
        _check_examples_nontrivial(parsed_doc),
        _check_return_type_documented(parsed_doc),
        _check_seealso_present(parsed_doc),
    ]


def deep_check_functions(
    target_names: list[str],
    docs_dir: str | Path,
    env: object,
) -> list[DeepFunctionResult]:
    """Run deep checks on a list of functions by name.

    Args:
        target_names: Function names to validate (e.g. ["ols", "meanc"]).
        docs_dir: Root directory of RST documentation.
        env: Sphinx-like environment with domaindata["gauss"]["objects"].

    Returns:
        List of DeepFunctionResult, one per function found.
    """
    docs_path = Path(docs_dir)
    gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})

    results: list[DeepFunctionResult] = []
    for name in target_names:
        if name not in gauss_objects:
            continue

        docname = gauss_objects[name]
        rst_file = docs_path / (docname + ".rst")

        if not rst_file.exists():
            continue

        content = rst_file.read_text(encoding="utf-8")
        parsed = parse_rst(str(rst_file), content, DocType.COMMAND_REF)
        checks = deep_check_function(parsed)
        overall = all(c.passed for c in checks)

        results.append(DeepFunctionResult(
            function_name=name,
            doc_page=docname,
            file_path=str(rst_file),
            checks=checks,
            overall_pass=overall,
        ))

    return results


def _check_signature_complete(parsed_doc: ParsedDoc) -> DeepCheckResult:
    """Check that all params in function signature have :param: docs."""
    # Extract param names from function directive signature
    sig_params = _extract_signature_params(parsed_doc)

    if not sig_params:
        return DeepCheckResult(
            check=DeepCheckType.SIGNATURE_COMPLETE,
            passed=True,
            detail="No parameters in signature",
        )

    # Find documented params from field_lists
    documented = set()
    for field in parsed_doc.field_lists:
        name = field["name"]
        if name.startswith("param "):
            param_name = name[len("param "):].strip()
            documented.add(param_name)

    missing = [p for p in sig_params if p not in documented]
    total = len(sig_params)
    doc_count = total - len(missing)

    if not missing:
        return DeepCheckResult(
            check=DeepCheckType.SIGNATURE_COMPLETE,
            passed=True,
            detail=f"{doc_count}/{total} params documented",
        )
    else:
        return DeepCheckResult(
            check=DeepCheckType.SIGNATURE_COMPLETE,
            passed=False,
            detail=f"Missing: {', '.join(missing)}",
        )


def _extract_signature_params(parsed_doc: ParsedDoc) -> list[str]:
    """Extract parameter names from function directive signature.

    Reuses the same system_message literal_block approach from
    SignatureChecker._signature_has_args().
    """
    for sys_msg in parsed_doc.raw_doc.findall(nodes.system_message):
        for lb in sys_msg.findall(nodes.literal_block):
            text = lb.astext()
            match = re.search(r"\.\.\s+function::\s*(.+)", text)
            if match:
                sig = match.group(1).strip()
                # Extract content between parentheses
                paren_match = re.search(r"\((.+)\)", sig)
                if paren_match:
                    params_str = paren_match.group(1)
                    # Split on commas, strip whitespace
                    # Handle "y = func(x, y)" -- the LHS assignment is before the func name
                    params = [p.strip() for p in params_str.split(",")]
                    # Filter out empty strings
                    return [p for p in params if p]
                return []
    return []


def _check_examples_nontrivial(parsed_doc: ParsedDoc) -> DeepCheckResult:
    """Check for non-trivial code examples (>20 chars content)."""
    if not parsed_doc.code_blocks:
        return DeepCheckResult(
            check=DeepCheckType.EXAMPLES_NONTRIVIAL,
            passed=False,
            detail="No code blocks found",
        )

    nontrivial = [
        cb for cb in parsed_doc.code_blocks
        if not cb.is_empty and len(cb.content.strip()) > 20
    ]

    if nontrivial:
        longest_lines = max(cb.content.count("\n") + 1 for cb in nontrivial)
        return DeepCheckResult(
            check=DeepCheckType.EXAMPLES_NONTRIVIAL,
            passed=True,
            detail=f"{len(nontrivial)} code blocks, longest is {longest_lines} lines",
        )
    else:
        return DeepCheckResult(
            check=DeepCheckType.EXAMPLES_NONTRIVIAL,
            passed=False,
            detail="Only trivial examples (< 20 chars)",
        )


def _check_return_type_documented(parsed_doc: ParsedDoc) -> DeepCheckResult:
    """Check for :return: or :rtype: field documentation."""
    has_return = any(
        field["name"].startswith("return") or field["name"].startswith("rtype")
        for field in parsed_doc.field_lists
    )

    if has_return:
        # Determine which type
        has_rtype = any(
            field["name"].startswith("rtype") for field in parsed_doc.field_lists
        )
        label = ":rtype:" if has_rtype else ":return:"
        return DeepCheckResult(
            check=DeepCheckType.RETURN_TYPE_DOCUMENTED,
            passed=True,
            detail=f"Has {label} field",
        )
    else:
        return DeepCheckResult(
            check=DeepCheckType.RETURN_TYPE_DOCUMENTED,
            passed=False,
            detail="No return type documentation",
        )


def _check_seealso_present(parsed_doc: ParsedDoc) -> DeepCheckResult:
    """Check for .. seealso:: directive in raw RST content."""
    try:
        raw_rst = Path(parsed_doc.path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # If we can't read the file, fail the check
        return DeepCheckResult(
            check=DeepCheckType.SEEALSO_PRESENT,
            passed=False,
            detail="Could not read RST file",
        )

    if SEEALSO_RE.search(raw_rst):
        return DeepCheckResult(
            check=DeepCheckType.SEEALSO_PRESENT,
            passed=True,
            detail="See Also section present",
        )
    else:
        return DeepCheckResult(
            check=DeepCheckType.SEEALSO_PRESENT,
            passed=False,
            detail="No See Also section",
        )

"""Scoring engine that combines cross-reference and blog mention signals.

Produces a ranked list of FunctionFrequency entries sorted by combined score.
"""

from __future__ import annotations

from gauss_doc_qa.frequency.models import FunctionFrequency


def rank_functions(
    env,
    doc_ref_counts: dict[str, int],
    blog_mention_counts: dict[str, int],
    doc_weight: float = 0.7,
    blog_weight: float = 0.3,
) -> list[FunctionFrequency]:
    """Combine doc cross-ref counts and blog mentions into a ranked list.

    Args:
        env: Sphinx BuildEnvironment with domaindata['gauss']['objects'].
        doc_ref_counts: Dict of function_name -> cross-reference count.
        blog_mention_counts: Dict of function_name -> blog mention count.
        doc_weight: Weight for doc cross-reference signal (default 0.7).
        blog_weight: Weight for blog mention signal (default 0.3).

    Returns:
        List of FunctionFrequency sorted by combined_score descending,
        then doc_refs descending, then name ascending.
    """
    gauss_objects = env.domaindata.get("gauss", {}).get("objects", {})

    rankings: list[FunctionFrequency] = []
    for func_name, (docname, _obj_type) in gauss_objects.items():
        doc_refs = doc_ref_counts.get(func_name, 0)
        blog_mentions = blog_mention_counts.get(func_name, 0)
        combined_score = doc_weight * doc_refs + blog_weight * blog_mentions

        rankings.append(FunctionFrequency(
            name=func_name,
            doc_refs=doc_refs,
            blog_mentions=blog_mentions,
            combined_score=combined_score,
            doc_page=docname,
        ))

    rankings.sort(key=lambda f: (-f.combined_score, -f.doc_refs, f.name))
    return rankings

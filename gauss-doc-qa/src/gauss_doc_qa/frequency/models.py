"""Data models for frequency ranking results."""

from dataclasses import dataclass


@dataclass
class FunctionFrequency:
    """Frequency ranking data for a single GAUSS function.

    Combines cross-reference counts from documentation and blog
    mention counts into a weighted combined score.
    """

    name: str  # function name (e.g. "ols")
    doc_refs: int  # count of :func: cross-references across all RST files
    blog_mentions: int  # count of mentions in aptech.com/blog posts
    combined_score: float  # weighted combined score
    doc_page: str  # docname from domaindata (e.g. "command_ref/ols")

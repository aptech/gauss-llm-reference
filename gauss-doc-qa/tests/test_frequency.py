"""Tests for the frequency ranking module."""

import json
import os
import tempfile
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from urllib.error import URLError

import pytest
from rich.console import Console

from gauss_doc_qa.frequency.models import FunctionFrequency
from gauss_doc_qa.frequency.counter import count_crossrefs
from gauss_doc_qa.frequency.blog_scraper import scrape_blog_mentions
from gauss_doc_qa.frequency.scorer import rank_functions
from gauss_doc_qa.frequency.report import (
    render_frequency_terminal,
    render_frequency_json,
    render_frequency_markdown,
)


def _make_env(objects: dict[str, tuple[str, str]]) -> SimpleNamespace:
    """Create a mock Sphinx environment with GAUSS domain objects."""
    return SimpleNamespace(
        domaindata={"gauss": {"objects": objects}}
    )


SAMPLE_OBJECTS = {
    "ols": ("command_ref/ols", "function"),
    "meanc": ("command_ref/meanc", "function"),
    "stdc": ("command_ref/stdc", "function"),
}


SAMPLE_RANKINGS = [
    FunctionFrequency(name="ols", doc_refs=42, blog_mentions=15, combined_score=33.9, doc_page="command_ref/ols"),
    FunctionFrequency(name="meanc", doc_refs=20, blog_mentions=8, combined_score=16.4, doc_page="command_ref/meanc"),
    FunctionFrequency(name="stdc", doc_refs=10, blog_mentions=3, combined_score=7.9, doc_page="command_ref/stdc"),
    FunctionFrequency(name="sumc", doc_refs=5, blog_mentions=1, combined_score=3.8, doc_page="command_ref/sumc"),
    FunctionFrequency(name="inv", doc_refs=2, blog_mentions=0, combined_score=1.4, doc_page="command_ref/inv"),
]


# -- Counter tests --

def test_count_crossrefs():
    """Cross-ref counter finds :func: references in RST files."""
    env = _make_env(SAMPLE_OBJECTS)

    with tempfile.TemporaryDirectory() as docs_dir:
        # Create an RST file that references ols and meanc
        ref_dir = os.path.join(docs_dir, "user_guide")
        os.makedirs(ref_dir)
        rst_path = os.path.join(ref_dir, "tutorial.rst")
        with open(rst_path, "w") as f:
            f.write("Use :func:`ols` for regression.\n")
            f.write("Compute means with :func:`meanc` and :func:`ols`.\n")
            f.write("Also see :func:`meanc`.\n")

        counts = count_crossrefs(docs_dir, env)

    assert counts["ols"] == 2
    assert counts["meanc"] == 2
    assert counts["stdc"] == 0


def test_count_crossrefs_excludes_self_refs():
    """Self-references (function's own page) should not be counted."""
    env = _make_env(SAMPLE_OBJECTS)

    with tempfile.TemporaryDirectory() as docs_dir:
        # Create the ols page that references itself
        cmd_dir = os.path.join(docs_dir, "command_ref")
        os.makedirs(cmd_dir)
        rst_path = os.path.join(cmd_dir, "ols.rst")
        with open(rst_path, "w") as f:
            f.write("OLS Function\n============\n\n")
            f.write("See also :func:`ols` for more details.\n")
            f.write("Compare with :func:`meanc`.\n")

        # Also create a separate file that references ols
        guide_dir = os.path.join(docs_dir, "guide")
        os.makedirs(guide_dir)
        guide_path = os.path.join(guide_dir, "intro.rst")
        with open(guide_path, "w") as f:
            f.write("Try :func:`ols` for OLS estimation.\n")

        counts = count_crossrefs(docs_dir, env)

    # Self-ref from ols.rst not counted, but guide/intro.rst ref counts
    assert counts["ols"] == 1
    # meanc referenced from ols.rst (not self), so it counts
    assert counts["meanc"] == 1


# -- Blog scraper tests --

def test_blog_scraper_handles_network_error():
    """Blog scraper returns empty dict when network fails."""
    with patch("gauss_doc_qa.frequency.blog_scraper.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = URLError("Network unreachable")
        result = scrape_blog_mentions({"ols", "meanc"})
    assert result == {}


def test_blog_scraper_extracts_mentions():
    """Blog scraper correctly counts function mentions from HTML pages."""
    listing_html = """
    <html><body>
    <a href="https://www.aptech.com/blog/intro-to-ols/">Intro to OLS</a>
    <a href="https://www.aptech.com/blog/mean-functions/">Mean Functions</a>
    </body></html>
    """

    post1_html = """
    <html><body>
    <p>In this post we use ols to run regression. The ols function is great.
    We also use meanc for column means.</p>
    </body></html>
    """

    post2_html = """
    <html><body>
    <p>The meanc function computes column means efficiently. Use meanc often.</p>
    </body></html>
    """

    responses = {
        "https://www.aptech.com/blog/": listing_html.encode("utf-8"),
        "https://www.aptech.com/blog/intro-to-ols/": post1_html.encode("utf-8"),
        "https://www.aptech.com/blog/mean-functions/": post2_html.encode("utf-8"),
    }

    def mock_urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if url not in responses:
            raise URLError(f"Not found: {url}")
        mock_resp = MagicMock()
        mock_resp.read.return_value = responses[url]
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    with patch("gauss_doc_qa.frequency.blog_scraper.urllib.request.urlopen", side_effect=mock_urlopen):
        with patch("gauss_doc_qa.frequency.blog_scraper.time.sleep"):
            result = scrape_blog_mentions({"ols", "meanc"}, max_pages=1)

    assert result.get("ols", 0) == 2  # 2 mentions in post1
    assert result.get("meanc", 0) == 3  # 1 in post1, 2 in post2


# -- Scorer tests --

def test_rank_functions():
    """Scorer combines doc refs and blog mentions with correct weights."""
    env = _make_env(SAMPLE_OBJECTS)
    doc_counts = {"ols": 10, "meanc": 5, "stdc": 0}
    blog_counts = {"ols": 3, "meanc": 8}

    result = rank_functions(env, doc_counts, blog_counts)

    assert len(result) == 3

    # ols: 0.7*10 + 0.3*3 = 7.9
    assert result[0].name == "ols"
    assert abs(result[0].combined_score - 7.9) < 0.01

    # meanc: 0.7*5 + 0.3*8 = 5.9
    assert result[1].name == "meanc"
    assert abs(result[1].combined_score - 5.9) < 0.01

    # stdc: 0.7*0 + 0.3*0 = 0.0
    assert result[2].name == "stdc"
    assert abs(result[2].combined_score - 0.0) < 0.01


# -- Report tests --

def test_render_frequency_terminal():
    """Terminal renderer produces table with function names and ranks."""
    buf = StringIO()
    console = Console(file=buf, no_color=True)
    render_frequency_terminal(SAMPLE_RANKINGS, console=console)
    output = buf.getvalue()

    assert "GAUSS Function Frequency Ranking" in output
    assert "ols" in output
    assert "meanc" in output
    assert "Total functions: 5" in output


def test_render_frequency_json():
    """JSON renderer produces valid JSON with correct structure."""
    result = render_frequency_json(SAMPLE_RANKINGS)
    parsed = json.loads(result)

    assert "total_functions" in parsed
    assert parsed["total_functions"] == 5
    assert "rankings" in parsed
    assert len(parsed["rankings"]) == 5
    assert parsed["rankings"][0]["name"] == "ols"
    assert parsed["rankings"][0]["rank"] == 1
    assert "doc_refs" in parsed["rankings"][0]
    assert "blog_mentions" in parsed["rankings"][0]
    assert "combined_score" in parsed["rankings"][0]


def test_render_frequency_markdown():
    """Markdown renderer produces table with headers and function names."""
    result = render_frequency_markdown(SAMPLE_RANKINGS)

    assert "# GAUSS Function Frequency Ranking" in result
    assert "**Total functions:** 5" in result
    assert "| Rank | Function | Doc Refs | Blog Mentions | Combined Score |" in result
    assert "| 1 | ols |" in result
    assert "| 2 | meanc |" in result


def test_top_n_slicing():
    """top_n parameter limits output to N entries across all formatters."""
    # JSON
    json_result = render_frequency_json(SAMPLE_RANKINGS, top_n=3)
    parsed = json.loads(json_result)
    assert len(parsed["rankings"]) == 3
    assert parsed["top_n"] == 3

    # Markdown
    md_result = render_frequency_markdown(SAMPLE_RANKINGS, top_n=3)
    assert "top 3" in md_result
    # Count table data rows (lines starting with "| N |")
    data_rows = [line for line in md_result.splitlines() if line.startswith("| ") and not line.startswith("| Rank") and not line.startswith("|---")]
    assert len(data_rows) == 3

    # Terminal
    buf = StringIO()
    console = Console(file=buf, no_color=True)
    render_frequency_terminal(SAMPLE_RANKINGS, top_n=3, console=console)
    output = buf.getvalue()
    assert "top 3" in output
    # Should have ols, meanc, stdc but not sumc, inv
    assert "sumc" not in output
    assert "inv" not in output

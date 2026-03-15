"""CLI integration tests for the freq subcommand."""

import json
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from gauss_doc_qa.frequency.models import FunctionFrequency


@pytest.fixture
def runner():
    return CliRunner()


def _make_mock_env(objects=None):
    """Create a mock Sphinx BuildEnvironment for freq tests."""
    if objects is None:
        objects = {
            "ols": ("command_ref/ols", "function"),
            "meanc": ("command_ref/meanc", "function"),
        }
    mock_env = MagicMock()
    mock_env.all_docs = {"test": 1234}
    mock_env.domaindata = {"gauss": {"objects": objects}}
    return mock_env


def _make_rankings(objects, doc_refs, blog_mentions, doc_weight=0.7, blog_weight=0.3):
    """Build FunctionFrequency list matching scorer logic."""
    rankings = []
    for name, (docname, _) in objects.items():
        dr = doc_refs.get(name, 0)
        bm = blog_mentions.get(name, 0)
        score = doc_weight * dr + blog_weight * bm
        rankings.append(FunctionFrequency(
            name=name, doc_refs=dr, blog_mentions=bm,
            combined_score=score, doc_page=docname,
        ))
    rankings.sort(key=lambda f: (-f.combined_score, -f.doc_refs, f.name))
    return rankings


@pytest.fixture(autouse=True)
def _mock_sphinx_module():
    """Ensure gauss_doc_qa.parser.sphinx_env is importable even without Sphinx."""
    mod_name = "gauss_doc_qa.parser.sphinx_env"
    if mod_name not in sys.modules:
        fake_mod = ModuleType(mod_name)
        fake_mod.load_sphinx_env = MagicMock()
        sys.modules[mod_name] = fake_mod
        # Also set it as an attribute on the parser package
        import gauss_doc_qa.parser as parser_pkg
        parser_pkg.sphinx_env = fake_mod
        yield
        sys.modules.pop(mod_name, None)
        if hasattr(parser_pkg, "sphinx_env"):
            delattr(parser_pkg, "sphinx_env")
    else:
        yield


# Patches target the module where the lazy import resolves
_PATCH_SPHINX = "gauss_doc_qa.parser.sphinx_env.load_sphinx_env"
_PATCH_COUNTER = "gauss_doc_qa.frequency.counter.count_crossrefs"
_PATCH_BLOG = "gauss_doc_qa.frequency.blog_scraper.scrape_blog_mentions"
_PATCH_SCORER = "gauss_doc_qa.frequency.scorer.rank_functions"


class TestFreqTerminal:

    def test_freq_terminal_output(self, runner):
        """freq with terminal format shows ranked output."""
        env = _make_mock_env()
        doc_refs = {"ols": 10, "meanc": 5}
        blog_refs = {"ols": 3}
        rankings = _make_rankings(env.domaindata["gauss"]["objects"], doc_refs, blog_refs)

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG, return_value=blog_refs), \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            assert "Ranked" in result.output
            assert "ols" in result.output
            assert "meanc" in result.output


class TestFreqJson:

    def test_freq_json_output(self, runner):
        """freq --format json produces valid JSON with rankings."""
        env = _make_mock_env()
        doc_refs = {"ols": 10, "meanc": 5}
        blog_refs = {"ols": 3}
        rankings = _make_rankings(env.domaindata["gauss"]["objects"], doc_refs, blog_refs)

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG, return_value=blog_refs), \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--format", "json", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            # Extract JSON (skip echo lines)
            lines = result.output.strip().split("\n")
            json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
            json_text = "\n".join(lines[json_start:])
            parsed = json.loads(json_text)
            assert "rankings" in parsed
            assert len(parsed["rankings"]) > 0
            entry = parsed["rankings"][0]
            assert "name" in entry
            assert "doc_refs" in entry
            assert "blog_mentions" in entry
            assert "combined_score" in entry


class TestFreqMarkdown:

    def test_freq_markdown_output(self, runner):
        """freq --format markdown produces markdown table."""
        env = _make_mock_env()
        doc_refs = {"ols": 10, "meanc": 5}
        blog_refs = {}
        rankings = _make_rankings(env.domaindata["gauss"]["objects"], doc_refs, blog_refs)

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG, return_value=blog_refs), \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--format", "markdown", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            assert "# GAUSS Function Frequency Ranking" in result.output
            assert "| Rank |" in result.output


class TestFreqTopN:

    def test_freq_top_n(self, runner):
        """freq --top-n 2 limits output to 2 functions."""
        objects = {
            "ols": ("command_ref/ols", "function"),
            "meanc": ("command_ref/meanc", "function"),
            "stdc": ("command_ref/stdc", "function"),
            "sumc": ("command_ref/sumc", "function"),
            "maxc": ("command_ref/maxc", "function"),
        }
        env = _make_mock_env(objects)
        doc_refs = {"ols": 10, "meanc": 8, "stdc": 6, "sumc": 4, "maxc": 2}
        blog_refs = {}
        rankings = _make_rankings(objects, doc_refs, blog_refs)

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG, return_value=blog_refs), \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--format", "json",
                "--top-n", "2", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            lines = result.output.strip().split("\n")
            json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
            json_text = "\n".join(lines[json_start:])
            parsed = json.loads(json_text)
            assert len(parsed["rankings"]) == 2


class TestFreqOutputTargets:

    def test_freq_output_targets_file(self, runner, tmp_path):
        """freq --output-targets writes function names to file."""
        objects = {
            "ols": ("command_ref/ols", "function"),
            "meanc": ("command_ref/meanc", "function"),
            "stdc": ("command_ref/stdc", "function"),
        }
        env = _make_mock_env(objects)
        doc_refs = {"ols": 10, "meanc": 5, "stdc": 3}
        blog_refs = {}
        rankings = _make_rankings(objects, doc_refs, blog_refs)

        target_file = str(tmp_path / "targets.txt")

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG, return_value=blog_refs), \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--no-blog",
                "--output-targets", target_file, "--top-n", "2",
            ])
            assert result.exit_code == 0, result.output
            assert Path(target_file).exists()
            lines = Path(target_file).read_text().strip().split("\n")
            assert len(lines) == 2
            # Each line is a function name
            for line in lines:
                assert line.strip() in objects


class TestFreqNoBlog:

    def test_freq_no_blog(self, runner):
        """freq --no-blog skips blog scraping entirely."""
        env = _make_mock_env()
        doc_refs = {"ols": 10, "meanc": 5}
        rankings = _make_rankings(env.domaindata["gauss"]["objects"], doc_refs, {})

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG) as mock_blog, \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            mock_blog.assert_not_called()
            assert "Skipping blog scraping" in result.output


class TestFreqCustomWeights:

    def test_freq_custom_weights(self, runner):
        """freq --doc-weight 0.5 --blog-weight 0.5 passes weights to scorer."""
        env = _make_mock_env()
        doc_refs = {"ols": 10, "meanc": 5}
        rankings = _make_rankings(env.domaindata["gauss"]["objects"], doc_refs, {},
                                  doc_weight=0.5, blog_weight=0.5)

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_SCORER, return_value=rankings) as mock_rank:
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--no-blog",
                "--doc-weight", "0.5", "--blog-weight", "0.5",
            ])
            assert result.exit_code == 0, result.output
            mock_rank.assert_called_once()
            call_args = mock_rank.call_args
            # rank_functions(env, doc_ref_counts, blog_mention_counts, doc_weight, blog_weight)
            assert call_args[0][3] == 0.5  # doc_weight
            assert call_args[0][4] == 0.5  # blog_weight


class TestFreqOutputFile:

    def test_freq_output_file(self, runner, tmp_path):
        """freq --output writes report to file."""
        env = _make_mock_env()
        doc_refs = {"ols": 10, "meanc": 5}
        rankings = _make_rankings(env.domaindata["gauss"]["objects"], doc_refs, {})

        output_file = str(tmp_path / "report.json")

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value=doc_refs), \
             patch(_PATCH_BLOG, return_value={}), \
             patch(_PATCH_SCORER, return_value=rankings):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "freq", "--no-blog",
                "--format", "json", "--output", output_file,
            ])
            assert result.exit_code == 0, result.output
            assert Path(output_file).exists()
            content = Path(output_file).read_text()
            parsed = json.loads(content)
            assert "rankings" in parsed

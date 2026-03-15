"""CLI integration tests for the deep-validate subcommand."""

import json
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from gauss_doc_qa.deep.models import DeepCheckResult, DeepCheckType, DeepFunctionResult
from gauss_doc_qa.frequency.models import FunctionFrequency


@pytest.fixture
def runner():
    return CliRunner()


def _make_mock_env(objects=None):
    """Create a mock Sphinx BuildEnvironment."""
    if objects is None:
        objects = {
            "ols": ("command_ref/ols", "function"),
            "meanc": ("command_ref/meanc", "function"),
        }
    mock_env = MagicMock()
    mock_env.all_docs = {"test": 1234}
    mock_env.domaindata = {"gauss": {"objects": objects}}
    return mock_env


def _make_deep_results(names=None, all_pass=True):
    """Build synthetic DeepFunctionResult list."""
    if names is None:
        names = ["ols", "meanc"]
    results = []
    for name in names:
        checks = [
            DeepCheckResult(
                check=DeepCheckType.SIGNATURE_COMPLETE,
                passed=True,
                detail="2/2 params documented",
            ),
            DeepCheckResult(
                check=DeepCheckType.EXAMPLES_NONTRIVIAL,
                passed=all_pass,
                detail="1 code blocks, longest is 5 lines" if all_pass else "No code blocks found",
            ),
            DeepCheckResult(
                check=DeepCheckType.RETURN_TYPE_DOCUMENTED,
                passed=True,
                detail="Has :rtype: field",
            ),
            DeepCheckResult(
                check=DeepCheckType.SEEALSO_PRESENT,
                passed=True,
                detail="See Also section present",
            ),
        ]
        results.append(DeepFunctionResult(
            function_name=name,
            doc_page=f"command_ref/{name}",
            file_path=f"/tmp/docs/command_ref/{name}.rst",
            checks=checks,
            overall_pass=all(c.passed for c in checks),
        ))
    return results


def _make_rankings(names, doc_refs=None):
    """Build FunctionFrequency list for freq ranking mock."""
    if doc_refs is None:
        doc_refs = {n: 10 - i for i, n in enumerate(names)}
    rankings = []
    for name in names:
        dr = doc_refs.get(name, 0)
        rankings.append(FunctionFrequency(
            name=name, doc_refs=dr, blog_mentions=0,
            combined_score=0.7 * dr, doc_page=f"command_ref/{name}",
        ))
    rankings.sort(key=lambda f: (-f.combined_score, f.name))
    return rankings


@pytest.fixture(autouse=True)
def _mock_sphinx_module():
    """Ensure gauss_doc_qa.parser.sphinx_env is importable even without Sphinx."""
    mod_name = "gauss_doc_qa.parser.sphinx_env"
    if mod_name not in sys.modules:
        fake_mod = ModuleType(mod_name)
        fake_mod.load_sphinx_env = MagicMock()
        sys.modules[mod_name] = fake_mod
        import gauss_doc_qa.parser as parser_pkg
        parser_pkg.sphinx_env = fake_mod
        yield
        sys.modules.pop(mod_name, None)
        if hasattr(parser_pkg, "sphinx_env"):
            delattr(parser_pkg, "sphinx_env")
    else:
        yield


_PATCH_SPHINX = "gauss_doc_qa.parser.sphinx_env.load_sphinx_env"
_PATCH_COUNTER = "gauss_doc_qa.frequency.counter.count_crossrefs"
_PATCH_BLOG = "gauss_doc_qa.frequency.blog_scraper.scrape_blog_mentions"
_PATCH_SCORER = "gauss_doc_qa.frequency.scorer.rank_functions"
_PATCH_DEEP_CHECK = "gauss_doc_qa.deep.checker.deep_check_functions"
_PATCH_AI_BATCH = "gauss_doc_qa.deep.ai_checker.ai_check_examples_batch"


class TestDeepValidateNoAi:

    def test_no_ai_runs_structural_only(self, runner):
        """deep-validate --no-ai runs structural checks, skips AI."""
        env = _make_mock_env()
        results = _make_deep_results()
        rankings = _make_rankings(["ols", "meanc"])

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value={"ols": 10, "meanc": 5}), \
             patch(_PATCH_SCORER, return_value=rankings), \
             patch(_PATCH_DEEP_CHECK, return_value=results), \
             patch(_PATCH_AI_BATCH) as mock_ai:
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate", "--no-ai", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            mock_ai.assert_not_called()
            assert "Skipping AI checks" in result.output
            assert "Deep validation:" in result.output


class TestDeepValidateTargetsFile:

    def test_targets_file_reads_names(self, runner, tmp_path):
        """deep-validate --targets-file reads function names from file."""
        env = _make_mock_env()
        results = _make_deep_results(["ols", "meanc"])

        targets = tmp_path / "targets.txt"
        targets.write_text("ols\nmeanc\n")

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_DEEP_CHECK, return_value=results) as mock_deep:
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate",
                "--targets-file", str(targets), "--no-ai",
            ])
            assert result.exit_code == 0, result.output
            assert "Loaded 2 target functions" in result.output
            # Verify deep_check_functions was called with correct names
            call_args = mock_deep.call_args
            assert "ols" in call_args[0][0]
            assert "meanc" in call_args[0][0]


class TestDeepValidateTopN:

    def test_top_n_limits_functions(self, runner):
        """deep-validate --top-n=2 limits to 2 functions."""
        all_names = ["ols", "meanc", "stdc", "sumc", "maxc"]
        objects = {n: (f"command_ref/{n}", "function") for n in all_names}
        env = _make_mock_env(objects)
        # Only top 2 results
        results = _make_deep_results(["ols", "meanc"])
        rankings = _make_rankings(all_names)

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value={n: 10 - i for i, n in enumerate(all_names)}), \
             patch(_PATCH_SCORER, return_value=rankings), \
             patch(_PATCH_DEEP_CHECK, return_value=results) as mock_deep:
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate",
                "--top-n", "2", "--no-ai", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            # Verify only 2 target names were passed
            call_args = mock_deep.call_args
            assert len(call_args[0][0]) == 2


class TestDeepValidateJsonOutput:

    def test_json_format(self, runner):
        """deep-validate --format=json produces valid JSON."""
        env = _make_mock_env()
        results = _make_deep_results()
        rankings = _make_rankings(["ols", "meanc"])

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value={"ols": 10, "meanc": 5}), \
             patch(_PATCH_SCORER, return_value=rankings), \
             patch(_PATCH_DEEP_CHECK, return_value=results):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate",
                "--format", "json", "--no-ai", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            # Extract JSON from output (skip status echo lines)
            lines = result.output.strip().split("\n")
            json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
            json_text = "\n".join(lines[json_start:])
            # Remove trailing summary line if present
            try:
                parsed = json.loads(json_text)
            except json.JSONDecodeError:
                # Summary line after JSON, trim it
                json_end = json_text.rfind("}")
                json_text = json_text[:json_end + 1]
                parsed = json.loads(json_text)
            assert "summary" in parsed
            assert "functions" in parsed


class TestDeepValidateMarkdownOutput:

    def test_markdown_format(self, runner):
        """deep-validate --format=markdown produces markdown table."""
        env = _make_mock_env()
        results = _make_deep_results()
        rankings = _make_rankings(["ols", "meanc"])

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value={"ols": 10, "meanc": 5}), \
             patch(_PATCH_SCORER, return_value=rankings), \
             patch(_PATCH_DEEP_CHECK, return_value=results):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate",
                "--format", "markdown", "--no-ai", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            assert "# Deep Validation Report" in result.output
            assert "| Function |" in result.output


class TestDeepValidateOutputFile:

    def test_output_to_file(self, runner, tmp_path):
        """deep-validate --output writes report to file."""
        env = _make_mock_env()
        results = _make_deep_results()
        rankings = _make_rankings(["ols", "meanc"])
        output_file = str(tmp_path / "report.json")

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value={"ols": 10, "meanc": 5}), \
             patch(_PATCH_SCORER, return_value=rankings), \
             patch(_PATCH_DEEP_CHECK, return_value=results):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate",
                "--format", "json", "--output", output_file,
                "--no-ai", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            assert Path(output_file).exists()
            content = Path(output_file).read_text()
            parsed = json.loads(content)
            assert "summary" in parsed


class TestDeepValidateNoApiKey:

    def test_no_api_key_shows_warning(self, runner):
        """deep-validate without ANTHROPIC_API_KEY shows warning."""
        env = _make_mock_env()
        results = _make_deep_results()
        rankings = _make_rankings(["ols", "meanc"])

        with patch(_PATCH_SPHINX, return_value=env), \
             patch(_PATCH_COUNTER, return_value={"ols": 10, "meanc": 5}), \
             patch(_PATCH_SCORER, return_value=rankings), \
             patch(_PATCH_DEEP_CHECK, return_value=results), \
             patch.dict("os.environ", {}, clear=True):
            from gauss_doc_qa.cli import cli
            result = runner.invoke(cli, [
                "--docs-dir", "/tmp", "deep-validate", "--no-blog",
            ])
            assert result.exit_code == 0, result.output
            assert "ANTHROPIC_API_KEY not set" in result.output

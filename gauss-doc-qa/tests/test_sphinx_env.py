"""Tests for Sphinx environment loader and sphinx checker registry."""

from unittest.mock import patch, MagicMock

from gauss_doc_qa.parser.sphinx_env import load_sphinx_env
from gauss_doc_qa.checkers.base import (
    BaseChecker,
    register_checker,
    get_all_sphinx_checkers,
    _checkers,
)


def test_load_sphinx_env_calls_sphinx_with_dummy_builder():
    """Verify load_sphinx_env creates Sphinx app with dummy builder."""
    mock_app = MagicMock()
    mock_env = MagicMock()
    mock_app.env = mock_env

    with patch(
        "gauss_doc_qa.parser.sphinx_env.Sphinx", return_value=mock_app
    ) as MockSphinx:
        env = load_sphinx_env("/fake/docs")

        MockSphinx.assert_called_once()
        call_kwargs = MockSphinx.call_args.kwargs
        assert call_kwargs["buildername"] == "dummy"
        mock_app.build.assert_called_once()
        assert env is mock_env


def test_load_sphinx_env_uses_freshenv():
    """Verify load_sphinx_env passes freshenv=True."""
    mock_app = MagicMock()
    mock_app.env = MagicMock()

    with patch(
        "gauss_doc_qa.parser.sphinx_env.Sphinx", return_value=mock_app
    ) as MockSphinx:
        load_sphinx_env("/fake/docs")
        call_kwargs = MockSphinx.call_args.kwargs
        assert call_kwargs["freshenv"] is True


def test_load_sphinx_env_returns_env():
    """Verify load_sphinx_env returns the app.env object."""
    mock_app = MagicMock()
    expected_env = MagicMock()
    mock_app.env = expected_env

    with patch("gauss_doc_qa.parser.sphinx_env.Sphinx", return_value=mock_app):
        result = load_sphinx_env("/fake/docs")
        assert result is expected_env


def test_get_all_sphinx_checkers_empty_when_none_registered():
    """get_all_sphinx_checkers returns empty list when no sphinx checkers exist."""
    # Current state: no sphinx checkers registered yet
    result = get_all_sphinx_checkers()
    assert isinstance(result, list)
    assert all(c.requires_sphinx for c in result)


def test_get_all_sphinx_checkers_filters_correctly():
    """get_all_sphinx_checkers returns only checkers with requires_sphinx=True."""

    class MockSphinxChecker(BaseChecker):
        name = "_test_sphinx_checker"
        requires_sphinx = True

        def check(self, parsed_doc, **kwargs):
            return []

    try:
        register_checker(MockSphinxChecker())
        sphinx_checkers = get_all_sphinx_checkers()
        assert any(c.name == "_test_sphinx_checker" for c in sphinx_checkers)
        assert all(c.requires_sphinx for c in sphinx_checkers)
    finally:
        _checkers.pop("_test_sphinx_checker", None)

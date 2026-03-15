"""Tests for the fixer verify module."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from gauss_doc_qa.fixer.verify import verify_sphinx_build


def _make_mock_sphinx_cls(statuscode=0, warning_text=""):
    """Create a mock Sphinx class that writes warnings and sets statuscode."""
    def factory(**kwargs):
        warning = kwargs.get("warning")
        if warning and warning_text:
            warning.write(warning_text)
        mock_app = MagicMock()
        mock_app.statuscode = statuscode
        return mock_app
    return factory


class TestVerifySphinxBuild:
    """Tests for verify_sphinx_build()."""

    @patch("gauss_doc_qa.fixer.verify._get_sphinx_cls")
    def test_verify_returns_dict(self, mock_get_cls):
        """Return structure should have success, warning_count, warnings keys."""
        mock_get_cls.return_value = _make_mock_sphinx_cls()

        result = verify_sphinx_build("/fake/docs")

        assert "success" in result
        assert "warning_count" in result
        assert "warnings" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["warning_count"], int)
        assert isinstance(result["warnings"], list)

    @patch("gauss_doc_qa.fixer.verify._get_sphinx_cls")
    def test_verify_captures_warnings(self, mock_get_cls):
        """Warnings written to the warning stream should appear in result."""
        warning_text = (
            "test.rst:5: WARNING: broken ref\n"
            "test.rst:10: WARNING: unknown role\n"
        )
        mock_get_cls.return_value = _make_mock_sphinx_cls(
            statuscode=0, warning_text=warning_text
        )

        result = verify_sphinx_build("/fake/docs")

        assert result["success"] is True
        assert result["warning_count"] == 2
        assert any("broken ref" in w for w in result["warnings"])
        assert any("unknown role" in w for w in result["warnings"])

    @patch("gauss_doc_qa.fixer.verify._get_sphinx_cls")
    def test_verify_build_failure(self, mock_get_cls):
        """Build failure should set success=False."""
        mock_get_cls.return_value = _make_mock_sphinx_cls(statuscode=1)

        result = verify_sphinx_build("/fake/docs")

        assert result["success"] is False

    @patch("gauss_doc_qa.fixer.verify._get_sphinx_cls")
    def test_verify_build_exception(self, mock_get_cls):
        """Exception during build should set success=False."""
        def raise_error(**kwargs):
            raise RuntimeError("build failed")
        mock_get_cls.return_value = raise_error

        result = verify_sphinx_build("/fake/docs")

        assert result["success"] is False

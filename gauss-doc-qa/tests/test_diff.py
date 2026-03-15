"""Tests for diff-mode filtering module."""

import os
import subprocess
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from gauss_doc_qa.diff import parse_since, filter_by_date, filter_by_svn_revision
from gauss_doc_qa.models import DocType


# --- parse_since tests ---

class TestParseSince:
    def test_date_string(self):
        mode, value = parse_since("2026-03-01")
        assert mode == "date"
        assert value == datetime(2026, 3, 1)

    def test_date_string_different_date(self):
        mode, value = parse_since("2025-12-31")
        assert mode == "date"
        assert value == datetime(2025, 12, 31)

    def test_svn_revision_lowercase(self):
        mode, value = parse_since("r12345")
        assert mode == "svn"
        assert value == 12345

    def test_svn_revision_uppercase(self):
        mode, value = parse_since("R12345")
        assert mode == "svn"
        assert value == 12345

    def test_svn_revision_large(self):
        mode, value = parse_since("r999999")
        assert mode == "svn"
        assert value == 999999

    def test_invalid_garbage(self):
        with pytest.raises(ValueError, match="--since must be"):
            parse_since("garbage")

    def test_invalid_empty(self):
        with pytest.raises(ValueError, match="--since must be"):
            parse_since("")

    def test_invalid_partial_date(self):
        with pytest.raises(ValueError, match="--since must be"):
            parse_since("2026-03")

    def test_invalid_r_no_digits(self):
        with pytest.raises(ValueError, match="--since must be"):
            parse_since("rabc")


# --- filter_by_date tests ---

class TestFilterByDate:
    def test_filters_old_files(self, tmp_path):
        """Files with mtime before cutoff are excluded."""
        old_file = tmp_path / "old.rst"
        new_file = tmp_path / "new.rst"
        old_file.write_text("old content")
        new_file.write_text("new content")

        # Set old file mtime to 2020
        old_time = datetime(2020, 1, 1).timestamp()
        os.utime(str(old_file), (old_time, old_time))

        # Set new file mtime to 2026
        new_time = datetime(2026, 3, 10).timestamp()
        os.utime(str(new_file), (new_time, new_time))

        file_list = [
            (str(old_file), DocType.COMMAND_REF),
            (str(new_file), DocType.COMMAND_REF),
        ]

        cutoff = datetime(2025, 1, 1)
        result = filter_by_date(file_list, cutoff)

        assert len(result) == 1
        assert result[0][0] == str(new_file)

    def test_includes_file_at_exact_cutoff(self, tmp_path):
        """File with mtime exactly at cutoff is included."""
        f = tmp_path / "exact.rst"
        f.write_text("content")

        cutoff = datetime(2026, 3, 1)
        os.utime(str(f), (cutoff.timestamp(), cutoff.timestamp()))

        file_list = [(str(f), DocType.OTHER)]
        result = filter_by_date(file_list, cutoff)
        assert len(result) == 1

    def test_empty_list(self):
        result = filter_by_date([], datetime(2026, 1, 1))
        assert result == []

    def test_preserves_order(self, tmp_path):
        """Filtered result preserves original list order."""
        files = []
        for name in ["a.rst", "b.rst", "c.rst"]:
            f = tmp_path / name
            f.write_text("content")
            new_time = datetime(2026, 3, 10).timestamp()
            os.utime(str(f), (new_time, new_time))
            files.append((str(f), DocType.COMMAND_REF))

        result = filter_by_date(files, datetime(2026, 1, 1))
        assert len(result) == 3
        assert [os.path.basename(r[0]) for r in result] == ["a.rst", "b.rst", "c.rst"]


# --- filter_by_svn_revision tests ---

class TestFilterBySvnRevision:
    def test_filters_to_changed_files(self):
        """Only files appearing in svn diff output are kept."""
        svn_output = (
            "M       /home/user/docs/func1.rst\n"
            "A       /home/user/docs/func2.rst\n"
        )
        mock_result = MagicMock()
        mock_result.stdout = svn_output

        file_list = [
            ("/home/user/docs/func1.rst", DocType.COMMAND_REF),
            ("/home/user/docs/func2.rst", DocType.COMMAND_REF),
            ("/home/user/docs/func3.rst", DocType.COMMAND_REF),
        ]

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = filter_by_svn_revision(file_list, 12345, "/home/user/docs")

        assert len(result) == 2
        assert result[0][0] == "/home/user/docs/func1.rst"
        assert result[1][0] == "/home/user/docs/func2.rst"

        mock_run.assert_called_once_with(
            ["svn", "diff", "--summarize", "-r", "12345:HEAD", "/home/user/docs"],
            capture_output=True, text=True, check=True,
        )

    def test_no_matches(self):
        """When svn output has no overlap with file_list, returns empty."""
        mock_result = MagicMock()
        mock_result.stdout = "M       /other/path/file.rst\n"

        file_list = [
            ("/home/user/docs/func1.rst", DocType.COMMAND_REF),
        ]

        with patch("subprocess.run", return_value=mock_result):
            result = filter_by_svn_revision(file_list, 100, "/home/user/docs")

        assert result == []

    def test_svn_command_failure(self):
        """CalledProcessError raises RuntimeError."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(
            1, "svn", stderr="svn: E155007: not a working copy"
        )):
            with pytest.raises(RuntimeError, match="not a working copy"):
                filter_by_svn_revision([], 100, "/not/svn/dir")

    def test_svn_not_installed(self):
        """FileNotFoundError raises RuntimeError about svn not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(RuntimeError, match="svn command not found"):
                filter_by_svn_revision([], 100, "/some/dir")

    def test_handles_multichar_status(self):
        """SVN diff --summarize can have multi-char status like 'MM'."""
        mock_result = MagicMock()
        mock_result.stdout = "MM      /docs/func1.rst\n"

        file_list = [("/docs/func1.rst", DocType.COMMAND_REF)]

        with patch("subprocess.run", return_value=mock_result):
            result = filter_by_svn_revision(file_list, 100, "/docs")

        assert len(result) == 1

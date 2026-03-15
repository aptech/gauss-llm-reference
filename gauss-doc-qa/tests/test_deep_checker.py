"""Tests for deep structural checker."""

import pytest

from gauss_doc_qa.deep.checker import deep_check_function
from gauss_doc_qa.deep.models import DeepCheckType, DeepFunctionResult
from gauss_doc_qa.models import DocType
from gauss_doc_qa.parser.rst_parser import parse_rst


# -- RST fixtures (inline) --------------------------------------------------

COMPLETE_FUNCTION_RST = """\
myabs
==============================================

Purpose
----------------

Returns the absolute value of *x*.

Format
----------------
.. function:: y = myabs(x)

    :param x: Input data.
    :type x: NxK matrix

    :return y: Contains the absolute values of *x*.
    :rtype y: NxK matrix

Examples
----------------

::

    x = { -1, 2, -3 };
    y = myabs(x);
    print y;

.. seealso::

    :func:`abs`
"""

MISSING_PARAMS_RST = """\
badsig
==============================================

Purpose
----------------

A function missing param docs.

Format
----------------
.. function:: y = badsig(x, z)

Examples
----------------

::

    y = badsig(x, z);
    print y;
"""

TRIVIAL_EXAMPLE_RST = """\
trivial
==============================================

Purpose
----------------

A function with trivial example.

Format
----------------
.. function:: y = trivial()

Examples
----------------

::

    y = trivial();
"""

NO_RETURN_RST = """\
noreturn
==============================================

Purpose
----------------

A function without return type documentation.

Format
----------------
.. function:: y = noreturn(x)

    :param x: Input data.

Examples
----------------

::

    x = { 1, 2, 3 };
    y = noreturn(x);
    print y;
"""

NO_SEEALSO_RST = """\
nosa
==============================================

Purpose
----------------

A function without See Also.

Format
----------------
.. function:: y = nosa(x)

    :param x: Input data.
    :return y: The result.
    :rtype y: matrix

Examples
----------------

::

    x = { 1, 2, 3 };
    y = nosa(x);
    print y;
"""


def _parse_from_file(tmp_path, filename, rst_content, doc_type=DocType.COMMAND_REF):
    """Write RST to a temp file and parse it (needed for seealso file read)."""
    rst_file = tmp_path / filename
    rst_file.write_text(rst_content, encoding="utf-8")
    return parse_rst(str(rst_file), rst_content, doc_type)


class TestAllChecksPassing:
    """Function with all 4 checks passing."""

    def test_complete_function_passes_all(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        assert len(checks) == 4
        assert all(c.passed for c in checks), (
            f"Expected all checks to pass, got: "
            f"{[(c.check.value, c.passed, c.detail) for c in checks]}"
        )

    def test_check_types_present(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        check_types = {c.check for c in checks}
        assert check_types == {
            DeepCheckType.SIGNATURE_COMPLETE,
            DeepCheckType.EXAMPLES_NONTRIVIAL,
            DeepCheckType.RETURN_TYPE_DOCUMENTED,
            DeepCheckType.SEEALSO_PRESENT,
        }


class TestSignatureComplete:
    """SIGNATURE_COMPLETE check."""

    def test_missing_params_fails(self, tmp_path):
        doc = _parse_from_file(tmp_path, "badsig.rst", MISSING_PARAMS_RST)
        checks = deep_check_function(doc)

        sig_check = next(c for c in checks if c.check == DeepCheckType.SIGNATURE_COMPLETE)
        assert sig_check.passed is False
        assert "Missing" in sig_check.detail
        assert "x" in sig_check.detail
        assert "z" in sig_check.detail

    def test_all_params_documented_passes(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        sig_check = next(c for c in checks if c.check == DeepCheckType.SIGNATURE_COMPLETE)
        assert sig_check.passed is True
        assert "1/1" in sig_check.detail


class TestExamplesNontrivial:
    """EXAMPLES_NONTRIVIAL check."""

    def test_trivial_example_fails(self, tmp_path):
        doc = _parse_from_file(tmp_path, "trivial.rst", TRIVIAL_EXAMPLE_RST)
        checks = deep_check_function(doc)

        ex_check = next(c for c in checks if c.check == DeepCheckType.EXAMPLES_NONTRIVIAL)
        assert ex_check.passed is False

    def test_substantive_example_passes(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        ex_check = next(c for c in checks if c.check == DeepCheckType.EXAMPLES_NONTRIVIAL)
        assert ex_check.passed is True
        assert "code blocks" in ex_check.detail


class TestReturnTypeDocumented:
    """RETURN_TYPE_DOCUMENTED check."""

    def test_no_return_type_fails(self, tmp_path):
        doc = _parse_from_file(tmp_path, "noreturn.rst", NO_RETURN_RST)
        checks = deep_check_function(doc)

        ret_check = next(c for c in checks if c.check == DeepCheckType.RETURN_TYPE_DOCUMENTED)
        assert ret_check.passed is False
        assert "No return type" in ret_check.detail

    def test_has_return_type_passes(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        ret_check = next(c for c in checks if c.check == DeepCheckType.RETURN_TYPE_DOCUMENTED)
        assert ret_check.passed is True


class TestSeeAlsoPresent:
    """SEEALSO_PRESENT check."""

    def test_no_seealso_fails(self, tmp_path):
        doc = _parse_from_file(tmp_path, "nosa.rst", NO_SEEALSO_RST)
        checks = deep_check_function(doc)

        sa_check = next(c for c in checks if c.check == DeepCheckType.SEEALSO_PRESENT)
        assert sa_check.passed is False
        assert "No See Also" in sa_check.detail

    def test_has_seealso_passes(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        sa_check = next(c for c in checks if c.check == DeepCheckType.SEEALSO_PRESENT)
        assert sa_check.passed is True


class TestOverallPass:
    """overall_pass should be False when any check fails."""

    def test_overall_pass_true_when_all_pass(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        overall = all(c.passed for c in checks)
        assert overall is True

    def test_overall_pass_false_when_any_fails(self, tmp_path):
        doc = _parse_from_file(tmp_path, "nosa.rst", NO_SEEALSO_RST)
        checks = deep_check_function(doc)

        overall = all(c.passed for c in checks)
        assert overall is False


class TestDeepFunctionResultToDict:
    """Serialization test."""

    def test_to_dict(self, tmp_path):
        doc = _parse_from_file(tmp_path, "myabs.rst", COMPLETE_FUNCTION_RST)
        checks = deep_check_function(doc)

        result = DeepFunctionResult(
            function_name="myabs",
            doc_page="command_ref/myabs",
            file_path=str(tmp_path / "myabs.rst"),
            checks=checks,
            overall_pass=all(c.passed for c in checks),
        )

        d = result.to_dict()
        assert d["function_name"] == "myabs"
        assert d["overall_pass"] is True
        assert len(d["checks"]) == 4
        assert all(isinstance(c["check"], str) for c in d["checks"])

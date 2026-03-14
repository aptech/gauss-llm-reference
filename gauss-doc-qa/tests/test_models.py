from gauss_doc_qa.models import Finding, Severity, DocType, CodeBlock


class TestSeverity:
    def test_error_value(self):
        assert Severity.ERROR.value == "error"

    def test_warning_value(self):
        assert Severity.WARNING.value == "warning"

    def test_info_value(self):
        assert Severity.INFO.value == "info"


class TestDocType:
    def test_command_ref_value(self):
        assert DocType.COMMAND_REF.value == "command_ref"

    def test_operator_value(self):
        assert DocType.OPERATOR.value == "operator"

    def test_alpha_index_value(self):
        assert DocType.ALPHA_INDEX.value == "alpha_index"

    def test_getting_started_value(self):
        assert DocType.GETTING_STARTED.value == "getting_started"

    def test_user_guide_value(self):
        assert DocType.USER_GUIDE.value == "user_guide"

    def test_graphics_guide_value(self):
        assert DocType.GRAPHICS_GUIDE.value == "graphics_guide"

    def test_app_module_value(self):
        assert DocType.APP_MODULE.value == "app_module"

    def test_include_fragment_value(self):
        assert DocType.INCLUDE_FRAGMENT.value == "include"

    def test_other_value(self):
        assert DocType.OTHER.value == "other"


class TestCodeBlock:
    def test_non_empty(self):
        cb = CodeBlock(content="x = 1;", line_number=10, is_empty=False)
        assert cb.content == "x = 1;"
        assert cb.line_number == 10
        assert cb.is_empty is False

    def test_empty(self):
        cb = CodeBlock(content="   ", line_number=5, is_empty=True)
        assert cb.is_empty is True

    def test_none_line_number(self):
        cb = CodeBlock(content="code", line_number=None, is_empty=False)
        assert cb.line_number is None


class TestFinding:
    def test_fields(self):
        f = Finding(
            file="test.rst",
            line=10,
            severity=Severity.ERROR,
            category="test_cat",
            checker="test_checker",
            message="test msg",
        )
        assert f.file == "test.rst"
        assert f.line == 10
        assert f.severity == Severity.ERROR
        assert f.category == "test_cat"
        assert f.checker == "test_checker"
        assert f.message == "test msg"
        assert f.auto_fixable is False

    def test_line_none(self):
        f = Finding(
            file="test.rst",
            line=None,
            severity=Severity.WARNING,
            category="cat",
            checker="chk",
            message="msg",
        )
        assert f.line is None

    def test_to_dict_severity_as_string(self):
        f = Finding(
            file="test.rst",
            line=10,
            severity=Severity.ERROR,
            category="test_cat",
            checker="test_checker",
            message="test msg",
        )
        d = f.to_dict()
        assert d["severity"] == "error"
        assert isinstance(d["severity"], str)

    def test_to_dict_warning_severity(self):
        f = Finding(
            file="x.rst",
            line=None,
            severity=Severity.WARNING,
            category="c",
            checker="k",
            message="m",
        )
        assert f.to_dict()["severity"] == "warning"

    def test_to_dict_info_severity(self):
        f = Finding(
            file="x.rst",
            line=1,
            severity=Severity.INFO,
            category="c",
            checker="k",
            message="m",
        )
        assert f.to_dict()["severity"] == "info"

    def test_to_dict_contains_all_fields(self):
        f = Finding(
            file="test.rst",
            line=10,
            severity=Severity.ERROR,
            category="test_cat",
            checker="test_checker",
            message="test msg",
        )
        d = f.to_dict()
        assert "file" in d
        assert "line" in d
        assert "severity" in d
        assert "category" in d
        assert "checker" in d
        assert "message" in d
        assert "auto_fixable" in d

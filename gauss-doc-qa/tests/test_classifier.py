from gauss_doc_qa.parser.classifier import classify_doc
from gauss_doc_qa.models import DocType


class TestClassifyDoc:
    def test_command_ref(self):
        assert classify_doc("docs/abs.rst", "docs") == DocType.COMMAND_REF

    def test_operator(self):
        assert classify_doc("docs/addition.rst", "docs") == DocType.OPERATOR

    def test_alpha_index_a(self):
        assert classify_doc("docs/a.rst", "docs") == DocType.ALPHA_INDEX

    def test_alpha_index_z(self):
        assert classify_doc("docs/z.rst", "docs") == DocType.ALPHA_INDEX

    def test_alpha_index_underscore(self):
        assert classify_doc("docs/_.rst", "docs") == DocType.ALPHA_INDEX

    def test_include_fragment(self):
        assert classify_doc("docs/include/plotattrremark.rst", "docs") == DocType.INCLUDE_FRAGMENT

    def test_getting_started(self):
        assert classify_doc("docs/getting-started/intro.rst", "docs") == DocType.GETTING_STARTED

    def test_user_guide(self):
        assert classify_doc("docs/user-guide/basics.rst", "docs") == DocType.USER_GUIDE

    def test_app_module_tsmt(self):
        assert classify_doc("docs/tsmt/arima.rst", "docs") == DocType.APP_MODULE

    def test_app_module_fanpac(self):
        assert classify_doc("docs/fanpac/factor.rst", "docs") == DocType.APP_MODULE

    def test_graphics_guide(self):
        assert classify_doc("docs/graphics-guide/scatter.rst", "docs") == DocType.GRAPHICS_GUIDE

    def test_nested_include(self):
        assert classify_doc("docs/include/sub/fragment.rst", "docs") == DocType.INCLUDE_FRAGMENT

    def test_deep_subdirectory_default(self):
        # Unknown subdirectory defaults to COMMAND_REF
        assert classify_doc("docs/unknown-dir/something.rst", "docs") == DocType.COMMAND_REF

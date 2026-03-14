import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def function_page_rst():
    return (FIXTURES_DIR / "function_page.rst").read_text()


@pytest.fixture
def operator_page_rst():
    return (FIXTURES_DIR / "operator_page.rst").read_text()


@pytest.fixture
def index_page_rst():
    return (FIXTURES_DIR / "index_page.rst").read_text()


@pytest.fixture
def include_fragment_rst():
    return (FIXTURES_DIR / "include_fragment.rst").read_text()


@pytest.fixture
def missing_code_rst():
    return (FIXTURES_DIR / "missing_code.rst").read_text()


@pytest.fixture
def empty_code_rst():
    return (FIXTURES_DIR / "empty_code.rst").read_text()


@pytest.fixture
def missing_sections_rst():
    return (FIXTURES_DIR / "missing_sections.rst").read_text()


@pytest.fixture
def incomplete_sig_rst():
    return (FIXTURES_DIR / "incomplete_sig.rst").read_text()

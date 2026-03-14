from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class DocType(Enum):
    COMMAND_REF = "command_ref"
    OPERATOR = "operator"
    ALPHA_INDEX = "alpha_index"
    GETTING_STARTED = "getting_started"
    USER_GUIDE = "user_guide"
    GRAPHICS_GUIDE = "graphics_guide"
    APP_MODULE = "app_module"
    INCLUDE_FRAGMENT = "include"
    OTHER = "other"


@dataclass
class CodeBlock:
    content: str
    line_number: int | None
    is_empty: bool


@dataclass
class Finding:
    file: str
    line: int | None
    severity: Severity
    category: str
    checker: str
    message: str
    auto_fixable: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class ParsedDoc:
    path: str
    doc_type: DocType
    title: str
    sections: list[str]          # normalized section titles (lowercase, stripped)
    code_blocks: list[CodeBlock]
    field_lists: list[dict]      # list of {name: str, body: str} from field_list nodes
    raw_doc: object              # docutils document node (for checkers that need deeper traversal)

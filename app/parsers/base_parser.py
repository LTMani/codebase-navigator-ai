import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class ExtractedParameter:
    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class ExtractedCall:
    callee_name: str
    line_number: int
    receiver: Optional[str] = None  # e.g. 'self', 'user_repo', 'Math'
    is_method_call: bool = False


@dataclass
class ExtractedFunction:
    name: str
    qualified_name: str
    start_line: int
    end_line: int
    line_count: int
    parameters: List[ExtractedParameter] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_static: bool = False
    is_method: bool = False
    visibility: str = "public"
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    parameter_count: int = 0
    return_count: int = 1
    docstring: Optional[str] = None
    calls: List[str] = field(default_factory=list)
    detailed_calls: List[ExtractedCall] = field(default_factory=list)


@dataclass
class ExtractedClass:
    name: str
    qualified_name: str
    start_line: int
    end_line: int
    line_count: int
    base_classes: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    methods: List[ExtractedFunction] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class ExtractedImport:
    module_name: str
    imported_names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    line_number: int = 1
    is_relative: bool = False
    is_external: bool = False
    resolved_path: Optional[str] = None


@dataclass
class ExtractedSymbol:
    name: str
    kind: str  # function, class, method, variable, constant, interface, type
    qualified_name: str
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0
    visibility: str = "public"
    signature: Optional[str] = None
    docstring: Optional[str] = None
    is_exported: bool = False


@dataclass
class ComplexityMetrics:
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    maintainability_index: float = 100.0
    documentation_ratio: float = 0.0


@dataclass
class ParseResult:
    language: str
    file_path: str
    symbols: List[ExtractedSymbol] = field(default_factory=list)
    functions: List[ExtractedFunction] = field(default_factory=list)
    classes: List[ExtractedClass] = field(default_factory=list)
    imports: List[ExtractedImport] = field(default_factory=list)
    metrics: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    purpose_summary: Optional[str] = None
    is_entry_point: bool = False
    is_test_file: bool = False
    is_config_file: bool = False
    layer_hint: Optional[str] = None  # presentation, api, service, domain, repository, infrastructure, utility
    errors: List[str] = field(default_factory=list)


class BaseParser(ABC):
    """Abstract Base Class for language AST parsers with standardized metric formulas."""

    @abstractmethod
    def parse(self, content: str, file_path: str) -> ParseResult:
        """Parse source code string and return structured AST analysis results."""
        pass

    @classmethod
    def calculate_line_counts(cls, content: str, comment_prefixes: tuple[str, ...] = ("#", "//", "/*", "*")) -> tuple[int, int, int, int]:
        """Calculate (total, code, comment, blank) lines."""
        lines = content.splitlines()
        total = len(lines)
        blank = 0
        comment = 0
        code = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank += 1
            elif any(stripped.startswith(prefix) for prefix in comment_prefixes):
                comment += 1
            else:
                code += 1

        return total, code, comment, blank

    @classmethod
    def calculate_maintainability_index(cls, halstead_volume: float, cyclomatic_complexity: int, lines_of_code: int) -> float:
        """
        Standard Maintainability Index (MI) formula:
        MI = max(0, (171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)) * 100 / 171)
        """
        loc = max(lines_of_code, 1)
        vol = max(halstead_volume, 1.0)
        cc = max(cyclomatic_complexity, 1)

        raw_mi = 171.0 - (5.2 * math.log(vol)) - (0.23 * cc) - (16.2 * math.log(loc))
        normalized_mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
        return round(normalized_mi, 2)

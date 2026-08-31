import re
from typing import Any, Dict, List, Optional
from app.parsers.base_parser import (
    BaseParser,
    ComplexityMetrics,
    ExtractedClass,
    ExtractedFunction,
    ExtractedImport,
    ExtractedSymbol,
    ParseResult,
)


class GoParser(BaseParser):
    """Parser for Go (.go) source files extracting packages, structs, interfaces, and receiver functions."""

    def __init__(self):
        super().__init__("Go")

    def parse(self, code_content: str, file_path: str = "") -> ParseResult:
        """Parse Go source code elements."""
        lines = code_content.splitlines()
        total_lines = len(lines)

        symbols: List[ExtractedSymbol] = []
        functions: List[ExtractedFunction] = []
        classes: List[ExtractedClass] = []
        imports: List[ExtractedImport] = []

        code_lines = 0
        comment_lines = 0
        in_block_comment = False

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            if in_block_comment:
                comment_lines += 1
                if "*/" in trimmed:
                    in_block_comment = False
                continue

            if trimmed.startswith("/*"):
                comment_lines += 1
                if "*/" not in trimmed:
                    in_block_comment = True
                continue

            if trimmed.startswith("//"):
                comment_lines += 1
                continue

            code_lines += 1

        # 1. Package & Imports
        pkg_pat = re.compile(r'^package\s+([a-zA-Z0-9_]+)')
        package_name = ""
        in_import_block = False

        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_pkg = pkg_pat.match(trimmed)
            if m_pkg:
                package_name = m_pkg.group(1)

            if trimmed == "import (":
                in_import_block = True
                continue
            elif in_import_block:
                if trimmed == ")":
                    in_import_block = False
                elif trimmed:
                    # e.g. "github.com/gin-gonic/gin"
                    mod = trimmed.strip('"').split()[-1].strip('"')
                    imports.append(ExtractedImport(module_name=mod, is_relative=False, line_number=i))
            elif trimmed.startswith("import "):
                mod = trimmed.replace("import", "").strip().strip('"')
                imports.append(ExtractedImport(module_name=mod, is_relative=False, line_number=i))

        # 2. Structs & Interfaces
        type_pat = re.compile(r'^type\s+([A-Za-z0-9_]+)\s+(struct|interface)')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_type = type_pat.match(trimmed)
            if m_type:
                name, kind = m_type.groups()
                is_exported = name[0].isupper()
                cls_obj = ExtractedClass(
                    name=name,
                    qualified_name=f"{package_name}.{name}" if package_name else name,
                    start_line=i,
                    end_line=min(i + 20, total_lines),
                    is_exported=is_exported,
                    line_count=20,
                )
                classes.append(cls_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind=kind,
                    qualified_name=f"{package_name}.{name}" if package_name else name,
                    start_line=i,
                    end_line=min(i + 20, total_lines),
                    is_exported=is_exported,
                    visibility="public" if is_exported else "private",
                ))

        # 3. Functions & Methods
        fn_pat = re.compile(r'^func\s+(?:\((?:[a-zA-Z0-9_*]+\s+)?\*?([A-Za-z0-9_]+)\)\s+)?([A-Za-z0-9_]+)\s*\(([^)]*)\)(?:\s*([^{]+))?')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_fn = fn_pat.match(trimmed)
            if m_fn:
                receiver, name, params_str, ret_type = m_fn.groups()
                params = [p.strip().split()[0] for p in params_str.split(",") if p.strip()]
                is_exported = name[0].isupper()
                qual = f"{receiver}.{name}" if receiver else name

                fn_obj = ExtractedFunction(
                    name=name,
                    qualified_name=qual,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    parameters=params,
                    return_type=ret_type.strip() if ret_type else None,
                    is_async=False,
                    is_exported=is_exported,
                    cyclomatic_complexity=self._estimate_cyclomatic_complexity(code_content),
                )
                functions.append(fn_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="method" if receiver else "function",
                    qualified_name=qual,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    is_exported=is_exported,
                    visibility="public" if is_exported else "private",
                ))

        # 4. Metrics
        h_metrics = self._calculate_halstead_metrics(code_content)
        cc = self._estimate_cyclomatic_complexity(code_content)
        mi = self._calculate_maintainability_index(h_metrics["volume"], cc, code_lines)

        complexity = ComplexityMetrics(
            cyclomatic_complexity=cc,
            cognitive_complexity=cc,
            halstead_volume=h_metrics["volume"],
            halstead_difficulty=h_metrics["difficulty"],
            halstead_effort=h_metrics["effort"],
            maintainability_index=mi,
            lines_of_code=code_lines,
            comment_lines=comment_lines,
            blank_lines=total_lines - code_lines - comment_lines,
        )

        return ParseResult(
            file_path=file_path,
            language=self.language,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=total_lines - code_lines - comment_lines,
            symbols=symbols,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity=complexity,
        )

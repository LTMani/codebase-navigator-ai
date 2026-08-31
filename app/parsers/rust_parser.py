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


class RustParser(BaseParser):
    """Parser for Rust (.rs) source code extracting structs, enums, traits, impl blocks, and functions."""

    def __init__(self):
        super().__init__("Rust")

    def parse(self, code_content: str, file_path: str = "") -> ParseResult:
        """Parse Rust source code."""
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

        # 1. Use / Mod statements
        use_pat = re.compile(r'^(?:pub\s+)?use\s+([a-zA-Z0-9_:]+)(?:::\{([^}]+)\})?;')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_use = use_pat.match(trimmed)
            if m_use:
                mod_path, items = m_use.groups()
                imported = [x.strip() for x in items.split(",")] if items else [mod_path.split("::")[-1]]
                imports.append(ExtractedImport(
                    module_name=mod_path,
                    imported_symbols=imported,
                    is_relative=mod_path.startswith("crate::") or mod_path.startswith("super::"),
                    line_number=i,
                ))

        # 2. Structs / Enums / Traits
        type_pat = re.compile(r'^(?:pub(?:\([^)]+\))?\s+)?(struct|enum|trait)\s+([A-Za-z0-9_]+)')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_type = type_pat.match(trimmed)
            if m_type:
                kind, name = m_type.groups()
                is_pub = "pub" in trimmed
                cls_obj = ExtractedClass(
                    name=name,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 20, total_lines),
                    is_exported=is_pub,
                    line_count=20,
                )
                classes.append(cls_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind=kind,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 20, total_lines),
                    is_exported=is_pub,
                    visibility="public" if is_pub else "private",
                ))

        # 3. Functions & Methods
        fn_pat = re.compile(r'^(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+([a-zA-Z0-9_]+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*->\s*([^{]+))?')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_fn = fn_pat.match(trimmed)
            if m_fn:
                name, params_str, ret_type = m_fn.groups()
                params = [p.strip().split(":")[0].strip() for p in params_str.split(",") if p.strip()]
                is_pub = "pub" in trimmed
                is_async = "async" in trimmed

                fn_obj = ExtractedFunction(
                    name=name,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    parameters=params,
                    return_type=ret_type.strip() if ret_type else None,
                    is_async=is_async,
                    is_exported=is_pub,
                    cyclomatic_complexity=self._estimate_cyclomatic_complexity(code_content),
                )
                functions.append(fn_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="function",
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    is_exported=is_pub,
                    visibility="public" if is_pub else "private",
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

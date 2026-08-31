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


class TypeScriptParser(BaseParser):
    """Deep structural and lexical parser for TypeScript (.ts, .tsx) source code."""

    def __init__(self):
        super().__init__("TypeScript")

    def parse(self, code_content: str, file_path: str = "") -> ParseResult:
        """Extract TypeScript interfaces, types, enums, classes, functions, and imports."""
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

        # 1. Imports
        import_patterns = [
            re.compile(r'import\s+(?:type\s+)?(?:(\w+)\s*,?\s*)?(?:\{([^}]+)\})?\s+from\s+[\'"]([^\'"]+)[\'"]'),
            re.compile(r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'),
            re.compile(r'import\s+[\'"]([^\'"]+)[\'"]'),
        ]

        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            for pat in import_patterns:
                m = pat.match(trimmed)
                if m:
                    groups = m.groups()
                    if len(groups) == 3:
                        default_sym, named_syms, mod_path = groups
                        symbols_list = []
                        if default_sym:
                            symbols_list.append(default_sym)
                        if named_syms:
                            symbols_list.extend([s.strip().split(" as ")[0].strip() for s in named_syms.split(",") if s.strip()])
                        is_rel = mod_path.startswith(".")
                        imports.append(ExtractedImport(
                            module_name=mod_path,
                            imported_symbols=symbols_list,
                            is_relative=is_rel,
                            line_number=i,
                        ))
                    break

        # 2. Interfaces & Types
        interface_pat = re.compile(r'^(?:export\s+)?interface\s+(\w+)(?:<[^>]+>)?(?:\s+extends\s+([^{]+))?')
        type_pat = re.compile(r'^(?:export\s+)?type\s+(\w+)(?:<[^>]+>)?\s*=')
        enum_pat = re.compile(r'^(?:export\s+)?(?:const\s+)?enum\s+(\w+)')

        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()

            m_if = interface_pat.match(trimmed)
            if m_if:
                name, extends_str = m_if.groups()
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="interface",
                    qualified_name=name,
                    start_line=i,
                    end_line=i + 5,
                    is_exported=trimmed.startswith("export"),
                    visibility="public",
                    metadata={"extends": extends_str.strip() if extends_str else None},
                ))

            m_type = type_pat.match(trimmed)
            if m_type:
                name = m_type.group(1)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="type_alias",
                    qualified_name=name,
                    start_line=i,
                    end_line=i,
                    is_exported=trimmed.startswith("export"),
                    visibility="public",
                ))

            m_enum = enum_pat.match(trimmed)
            if m_enum:
                name = m_enum.group(1)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="enum",
                    qualified_name=name,
                    start_line=i,
                    end_line=i + 5,
                    is_exported=trimmed.startswith("export"),
                    visibility="public",
                ))

        # 3. Classes
        class_pat = re.compile(r'^(?:export\s+)?(?:abstract\s+)?class\s+(\w+)(?:<[^>]+>)?(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_cls = class_pat.match(trimmed)
            if m_cls:
                name, extends_cls, implements_str = m_cls.groups()
                base_classes = []
                if extends_cls:
                    base_classes.append(extends_cls)
                if implements_str:
                    base_classes.extend([imp.strip() for imp in implements_str.split(",") if imp.strip()])

                cls_obj = ExtractedClass(
                    name=name,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 25, total_lines),
                    base_classes=base_classes,
                    is_exported=trimmed.startswith("export"),
                    line_count=25,
                )
                classes.append(cls_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="class",
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 25, total_lines),
                    is_exported=trimmed.startswith("export"),
                    visibility="public",
                ))

        # 4. Functions & Arrow Functions & Methods
        fn_patterns = [
            re.compile(r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?'),
            re.compile(r'^(?:export\s+)?(?:const|let)\s+(\w+)\s*(?::\s*[^=]+)?\s*=\s*(?:async\s*)?\(([^)]*)\)(?:\s*:\s*([^=]+))?\s*=>'),
            re.compile(r'^\s*(?:public|private|protected|async|static|\s)*(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?\s*\{'),
        ]

        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            for pat in fn_patterns:
                m_fn = pat.match(trimmed)
                if m_fn:
                    name, params_str, ret_type = m_fn.groups()
                    if name in ("if", "for", "while", "switch", "catch"):
                        continue

                    params = [p.strip().split(":")[0].strip() for p in params_str.split(",") if p.strip()]
                    is_async = "async" in trimmed
                    is_exp = trimmed.startswith("export")

                    fn_obj = ExtractedFunction(
                        name=name,
                        qualified_name=name,
                        start_line=i,
                        end_line=min(i + 15, total_lines),
                        parameters=params,
                        return_type=ret_type.strip() if ret_type else None,
                        is_async=is_async,
                        is_exported=is_exp,
                        cyclomatic_complexity=self._estimate_cyclomatic_complexity(code_content),
                    )
                    functions.append(fn_obj)
                    symbols.append(ExtractedSymbol(
                        name=name,
                        kind="function",
                        qualified_name=name,
                        start_line=i,
                        end_line=min(i + 15, total_lines),
                        is_exported=is_exp,
                        visibility="public",
                    ))
                    break

        # 5. Metrics
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

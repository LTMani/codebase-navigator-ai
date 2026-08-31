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


class JavaParser(BaseParser):
    """Parser for Java (.java) source files supporting Spring annotations, packages, classes, and methods."""

    def __init__(self):
        super().__init__("Java")

    def parse(self, code_content: str, file_path: str = "") -> ParseResult:
        """Parse Java classes, interfaces, records, methods, and Spring Boot annotations."""
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
        import_pat = re.compile(r'^import\s+(?:static\s+)?([a-zA-Z0-9_.*]+);')
        package_pat = re.compile(r'^package\s+([a-zA-Z0-9_.]+);')
        package_name = ""

        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            m_pkg = package_pat.match(trimmed)
            if m_pkg:
                package_name = m_pkg.group(1)

            m_imp = import_pat.match(trimmed)
            if m_imp:
                mod_path = m_imp.group(1)
                sym = mod_path.split(".")[-1]
                imports.append(ExtractedImport(
                    module_name=mod_path,
                    imported_symbols=[sym] if sym != "*" else [],
                    is_relative=False,
                    line_number=i,
                ))

        # 2. Classes / Interfaces / Records / Enums
        class_pat = re.compile(r'^(?:public|protected|private|abstract|final|static|\s)*\b(class|interface|enum|record)\s+([A-Za-z0-9_]+)(?:<[^>]+>)?(?:\s+extends\s+([A-Za-z0-9_.,\s<>]+))?(?:\s+implements\s+([A-Za-z0-9_.,\s<>]+))?')

        current_annotations = []
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            if trimmed.startswith("@"):
                current_annotations.append(trimmed)
                continue

            m_cls = class_pat.match(trimmed)
            if m_cls:
                kind, name, extends_str, implements_str = m_cls.groups()
                base_classes = []
                if extends_str:
                    base_classes.append(extends_str.strip())
                if implements_str:
                    base_classes.extend([imp.strip() for imp in implements_str.split(",") if imp.strip()])

                is_pub = "public" in trimmed
                qual_name = f"{package_name}.{name}" if package_name else name

                cls_obj = ExtractedClass(
                    name=name,
                    qualified_name=qual_name,
                    start_line=i,
                    end_line=min(i + 30, total_lines),
                    base_classes=base_classes,
                    is_exported=is_pub,
                    line_count=30,
                )
                classes.append(cls_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind=kind,
                    qualified_name=qual_name,
                    start_line=i,
                    end_line=min(i + 30, total_lines),
                    is_exported=is_pub,
                    visibility="public" if is_pub else "package-private",
                    metadata={"annotations": current_annotations.copy()},
                ))
                current_annotations = []
            elif not trimmed.startswith("@"):
                current_annotations = []

        # 3. Methods
        method_pat = re.compile(r'^(?:public|protected|private|static|final|abstract|synchronized|\s)*([A-Za-z0-9_<>[\]]+)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*throws\s+[^{]+)?\s*\{?')
        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()
            if trimmed.startswith("@") or trimmed.startswith("//") or trimmed.startswith("/*"):
                continue

            m_method = method_pat.match(trimmed)
            if m_method:
                ret_type, name, params_str = m_method.groups()
                if name in ("if", "for", "while", "switch", "catch", "return", "class"):
                    continue

                params = [p.strip().split()[-1] for p in params_str.split(",") if p.strip()]
                is_pub = "public" in trimmed

                fn_obj = ExtractedFunction(
                    name=name,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    parameters=params,
                    return_type=ret_type.strip(),
                    is_async=False,
                    is_exported=is_pub,
                    cyclomatic_complexity=self._estimate_cyclomatic_complexity(code_content),
                )
                functions.append(fn_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind="method",
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    is_exported=is_pub,
                    visibility="public" if is_pub else "package-private",
                ))

        # 4. Complexity & Metrics
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

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


class SQLParser(BaseParser):
    """Parser for SQL (.sql) schemas, migrations, views, and stored procedures."""

    def __init__(self):
        super().__init__("SQL")

    def parse(self, code_content: str, file_path: str = "") -> ParseResult:
        """Parse SQL tables, views, procedures, and foreign key references."""
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

            if trimmed.startswith("--"):
                comment_lines += 1
                continue

            code_lines += 1

        # 1. CREATE TABLE / VIEW
        table_pat = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?(TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`|")?([a-zA-Z0-9_]+)(?:`|")?', re.IGNORECASE)
        proc_pat = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?(PROCEDURE|FUNCTION)\s+(?:`|")?([a-zA-Z0-9_]+)(?:`|")?', re.IGNORECASE)
        fk_pat = re.compile(r'FOREIGN\s+KEY\s*\([^)]+\)\s*REFERENCES\s+([a-zA-Z0-9_]+)', re.IGNORECASE)

        for i, line in enumerate(lines, start=1):
            trimmed = line.strip()

            m_tbl = table_pat.search(trimmed)
            if m_tbl:
                kind, name = m_tbl.groups()
                cls_obj = ExtractedClass(
                    name=name,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 20, total_lines),
                    is_exported=True,
                    line_count=20,
                )
                classes.append(cls_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind=kind.lower(),
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 20, total_lines),
                    is_exported=True,
                    visibility="public",
                ))

            m_proc = proc_pat.search(trimmed)
            if m_proc:
                kind, name = m_proc.groups()
                fn_obj = ExtractedFunction(
                    name=name,
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    is_exported=True,
                    cyclomatic_complexity=1,
                )
                functions.append(fn_obj)
                symbols.append(ExtractedSymbol(
                    name=name,
                    kind=kind.lower(),
                    qualified_name=name,
                    start_line=i,
                    end_line=min(i + 15, total_lines),
                    is_exported=True,
                    visibility="public",
                ))

            m_fk = fk_pat.search(trimmed)
            if m_fk:
                ref_tbl = m_fk.group(1)
                imports.append(ExtractedImport(module_name=ref_tbl, is_relative=False, line_number=i))

        # 2. Metrics
        complexity = ComplexityMetrics(
            cyclomatic_complexity=1,
            cognitive_complexity=1,
            halstead_volume=100.0,
            halstead_difficulty=1.0,
            halstead_effort=100.0,
            maintainability_index=95.0,
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

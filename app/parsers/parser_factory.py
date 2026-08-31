from pathlib import Path
from typing import Dict, Optional, Type
from app.parsers.base_parser import BaseParser, ComplexityMetrics, ParseResult
from app.parsers.css_parser import CSSParser
from app.parsers.go_parser import GoParser
from app.parsers.html_parser import HTMLParser
from app.parsers.java_parser import JavaParser
from app.parsers.javascript_parser import JavaScriptParser
from app.parsers.python_parser import PythonParser
from app.parsers.rust_parser import RustParser
from app.parsers.sql_parser import SQLParser
from app.parsers.typescript_parser import TypeScriptParser


class GenericFallbackParser(BaseParser):
    """Fallback parser for text, markdown, json, yaml, or unsupported languages."""

    def __init__(self, language_name: str = "Plain Text"):
        super().__init__(language_name)

    def parse(self, content: str, file_path: str = "") -> ParseResult:
        lines = content.splitlines()
        total = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith(("#", "//", "/*", "--"))])
        comment_lines = len([l for l in lines if l.strip().startswith(("#", "//", "/*", "--"))])

        complexity = ComplexityMetrics(
            cyclomatic_complexity=1,
            cognitive_complexity=1,
            halstead_volume=50.0,
            halstead_difficulty=1.0,
            halstead_effort=50.0,
            maintainability_index=90.0,
            lines_of_code=code_lines,
            comment_lines=comment_lines,
            blank_lines=total - code_lines - comment_lines,
        )

        return ParseResult(
            file_path=file_path,
            language=self.language,
            total_lines=total,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=total - code_lines - comment_lines,
            complexity=complexity,
            purpose_summary=f"{self.language} data or source file.",
        )


class ParserFactory:
    """Factory creating and resolving AST parsers for specific file types."""

    _PARSERS: Dict[str, BaseParser] = {
        ".py": PythonParser(),
        ".pyw": PythonParser(),
        ".js": JavaScriptParser(),
        ".mjs": JavaScriptParser(),
        ".cjs": JavaScriptParser(),
        ".jsx": JavaScriptParser(),
        ".ts": TypeScriptParser(),
        ".tsx": TypeScriptParser(),
        ".java": JavaParser(),
        ".go": GoParser(),
        ".rs": RustParser(),
        ".sql": SQLParser(),
        ".html": HTMLParser(),
        ".htm": HTMLParser(),
        ".css": CSSParser(),
        ".scss": CSSParser(),
        ".sass": CSSParser(),
        ".less": CSSParser(),
    }

    _GENERIC_MAP: Dict[str, str] = {
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".toml": "TOML",
        ".md": "Markdown",
        ".sh": "Shell Script",
        ".bash": "Shell Script",
        ".zsh": "Shell Script",
        ".ps1": "PowerShell",
        ".txt": "Plain Text",
        ".csv": "CSV",
        ".xml": "XML",
        ".svg": "SVG",
        ".graphql": "GraphQL",
        ".gql": "GraphQL",
    }

    @classmethod
    def get_parser(cls, file_path: str) -> BaseParser:
        """Resolve parser instance based on file extension."""
        ext = Path(file_path).suffix.lower()
        if ext in cls._PARSERS:
            return cls._PARSERS[ext]
        
        lang_name = cls._GENERIC_MAP.get(ext, "Plain Text")
        return GenericFallbackParser(language_name=lang_name)

    @classmethod
    def parse_file(cls, content: str, file_path: str) -> ParseResult:
        """Convenience method to resolve parser and parse content."""
        parser = cls.get_parser(file_path)
        return parser.parse(content, file_path)

from pathlib import Path
from typing import Dict, Optional, Type
from app.parsers.base_parser import BaseParser, ComplexityMetrics, ParseResult
from app.parsers.css_parser import CSSParser
from app.parsers.html_parser import HTMLParser
from app.parsers.javascript_parser import JavaScriptParser
from app.parsers.python_parser import PythonParser


class GenericFallbackParser(BaseParser):
    """Fallback parser for text, markdown, json, yaml, sql, or unsupported languages."""

    def __init__(self, language_name: str = "Plain Text"):
        self.language_name = language_name

    def parse(self, content: str, file_path: str) -> ParseResult:
        result = ParseResult(language=self.language_name, file_path=file_path)
        total, code, comment, blank = self.calculate_line_counts(content)
        result.metrics = ComplexityMetrics(
            total_lines=total,
            code_lines=code,
            comment_lines=comment,
            blank_lines=blank,
            maintainability_index=85.0,
        )
        result.purpose_summary = f"{self.language_name} source or data file."
        return result


class ParserFactory:
    """Factory creating and resolving AST parsers for specific file types."""

    _PARSERS: Dict[str, BaseParser] = {
        ".py": PythonParser(),
        ".pyw": PythonParser(),
        ".js": JavaScriptParser(),
        ".mjs": JavaScriptParser(),
        ".cjs": JavaScriptParser(),
        ".jsx": JavaScriptParser(),
        ".ts": JavaScriptParser(),
        ".tsx": JavaScriptParser(),
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
        ".sql": "SQL",
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

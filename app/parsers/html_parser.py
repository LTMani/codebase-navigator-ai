import re
from typing import Any, Dict, List, Optional
from app.parsers.base_parser import (
    BaseParser,
    ComplexityMetrics,
    ExtractedImport,
    ExtractedSymbol,
    ParseResult,
)


class HTMLParser(BaseParser):
    """Semantic HTML5 and Template Parser extracting script/style dependencies and DOM structure."""

    def parse(self, content: str, file_path: str) -> ParseResult:
        result = ParseResult(language="HTML", file_path=file_path)
        result.layer_hint = "presentation"
        norm_path = file_path.replace("\\", "/").lower()

        total_lines, code_lines, comment_lines, blank_lines = self.calculate_line_counts(
            content, comment_prefixes=("<!--",)
        )

        if norm_path in ("index.html", "app.html", "main.html") or norm_path.endswith(("/index.html", "/app.html", "/main.html")):
            result.is_entry_point = True

        # Extract Script dependencies (<script src="...">)
        for match in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE):
            src = match.group(1).strip()
            line_no = content[: match.start()].count("\n") + 1
            result.imports.append(
                ExtractedImport(
                    module_name=src,
                    imported_names=["script"],
                    line_number=line_no,
                    is_relative=src.startswith(".") or not src.startswith("http"),
                    is_external=src.startswith("http"),
                )
            )

        # Extract Stylesheet dependencies (<link rel="stylesheet" href="...">)
        for match in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\']|<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE):
            href = (match.group(1) or match.group(2) or "").strip()
            if href:
                line_no = content[: match.start()].count("\n") + 1
                result.imports.append(
                    ExtractedImport(
                        module_name=href,
                        imported_names=["stylesheet"],
                        line_number=line_no,
                        is_relative=href.startswith(".") or not href.startswith("http"),
                        is_external=href.startswith("http"),
                    )
                )

        # Extract Form Action endpoints (<form action="...">)
        for match in re.finditer(r'<form[^>]+action=["\']([^"\']+)["\']', content, re.IGNORECASE):
            action = match.group(1).strip()
            line_no = content[: match.start()].count("\n") + 1
            result.symbols.append(
                ExtractedSymbol(
                    name=f"form:{action}",
                    kind="form_action",
                    qualified_name=f"form:{action}",
                    start_line=line_no,
                    end_line=line_no,
                )
            )

        # Extract Elements with IDs (<div id="...">)
        for match in re.finditer(r'id=["\']([a-zA-Z0-9_\-]+)["\']', content):
            elem_id = match.group(1).strip()
            line_no = content[: match.start()].count("\n") + 1
            result.symbols.append(
                ExtractedSymbol(
                    name=elem_id,
                    kind="dom_id",
                    qualified_name=f"#{elem_id}",
                    start_line=line_no,
                    end_line=line_no,
                )
            )

        # Basic complexity: number of interactive forms/elements and template directives
        tags_count = len(re.findall(r"<[a-zA-Z0-9\-]+", content))
        cyclomatic = max(1 + len(re.findall(r"{%\s*(if|for)\b|v-if|v-for|\*ngIf|\*ngFor", content)), 1)
        mi = self.calculate_maintainability_index(max(tags_count * 10.0, 1.0), cyclomatic, code_lines)

        result.metrics = ComplexityMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=cyclomatic,
            maintainability_index=mi,
            documentation_ratio=round(comment_lines / max(total_lines, 1), 3),
        )
        result.purpose_summary = f"HTML UI Template with {tags_count} DOM elements."

        return result

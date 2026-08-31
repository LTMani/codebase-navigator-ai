import re
from typing import Any, Dict, List, Optional
from app.parsers.base_parser import (
    BaseParser,
    ComplexityMetrics,
    ExtractedImport,
    ExtractedSymbol,
    ParseResult,
)


class CSSParser(BaseParser):
    """CSS3, SCSS, and PostCSS stylesheet parser extracting imports, variables, and rule structures."""

    def parse(self, content: str, file_path: str) -> ParseResult:
        result = ParseResult(language="CSS", file_path=file_path)
        result.layer_hint = "presentation"

        total_lines, code_lines, comment_lines, blank_lines = self.calculate_line_counts(
            content, comment_prefixes=("/*", "*")
        )

        # 1. Extract @import statements
        for match in re.finditer(r'@import\s+(?:url\()?[\'"]([^\'")]+)[\'"]\)?\s*;', content):
            imported_file = match.group(1).strip()
            line_no = content[: match.start()].count("\n") + 1
            result.imports.append(
                ExtractedImport(
                    module_name=imported_file,
                    imported_names=["css_import"],
                    line_number=line_no,
                    is_relative=imported_file.startswith(".") or not imported_file.startswith("http"),
                    is_external=imported_file.startswith("http"),
                )
            )

        # 2. Extract CSS Custom Properties / Variables (--custom-color: ...)
        for match in re.finditer(r'(--[a-zA-Z0-9_\-]+)\s*:\s*([^;]+);', content):
            var_name = match.group(1).strip()
            line_no = content[: match.start()].count("\n") + 1
            result.symbols.append(
                ExtractedSymbol(
                    name=var_name,
                    kind="css_variable",
                    qualified_name=var_name,
                    start_line=line_no,
                    end_line=line_no,
                )
            )

        # 3. Extract Keyframe Animations
        for match in re.finditer(r'@keyframes\s+([a-zA-Z0-9_\-]+)', content):
            anim_name = match.group(1).strip()
            line_no = content[: match.start()].count("\n") + 1
            result.symbols.append(
                ExtractedSymbol(
                    name=anim_name,
                    kind="animation",
                    qualified_name=f"@keyframes {anim_name}",
                    start_line=line_no,
                    end_line=line_no,
                )
            )

        # 4. Count Rules & Specificity
        rule_blocks = len(re.findall(r"\{[^\}]*\}", content))
        cyclomatic = max(1 + len(re.findall(r"@media|@supports", content)), 1)
        mi = self.calculate_maintainability_index(max(rule_blocks * 15.0, 1.0), cyclomatic, code_lines)

        result.metrics = ComplexityMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=cyclomatic,
            maintainability_index=mi,
            documentation_ratio=round(comment_lines / max(total_lines, 1), 3),
        )
        result.purpose_summary = f"Stylesheet with {rule_blocks} CSS rule declarations."

        return result

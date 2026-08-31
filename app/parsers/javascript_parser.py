import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from app.parsers.base_parser import (
    BaseParser,
    ComplexityMetrics,
    ExtractedCall,
    ExtractedClass,
    ExtractedFunction,
    ExtractedImport,
    ExtractedParameter,
    ExtractedSymbol,
    ParseResult,
)


class JavaScriptParser(BaseParser):
    """High-performance Lexical & Structural AST Parser for JavaScript, TypeScript, JSX, and TSX."""

    def parse(self, content: str, file_path: str) -> ParseResult:
        result = ParseResult(language="JavaScript", file_path=file_path)
        norm_path = file_path.replace("\\", "/").lower()

        if norm_path.endswith((".ts", ".tsx")):
            result.language = "TypeScript"

        total_lines, code_lines, comment_lines, blank_lines = self.calculate_line_counts(
            content, comment_prefixes=("//", "/*", "*")
        )

        is_test = any(t in norm_path for t in (".test.", ".spec.", "_test.", "_spec.", "/tests/", "/__tests__/"))
        is_config = any(c in norm_path for c in ("webpack.config", "vite.config", "rollup.config", "tsconfig", "package.json", "babel.config", "tailwind.config"))

        result.is_test_file = is_test
        result.is_config_file = is_config

        # Layer classification heuristics
        if any(seg in norm_path for seg in ("components", "views", "pages", "layouts", "screens", "ui", "templates")) or norm_path.endswith((".jsx", ".tsx")):
            result.layer_hint = "presentation"
        elif any(seg in norm_path for seg in ("routes", "controllers", "api", "endpoints", "handlers")):
            result.layer_hint = "api"
        elif any(seg in norm_path for seg in ("services", "managers", "usecases", "domain")):
            result.layer_hint = "service"
        elif any(seg in norm_path for seg in ("models", "entities", "schemas", "types", "interfaces")):
            result.layer_hint = "domain"
        elif any(seg in norm_path for seg in ("repositories", "db", "database", "dao", "prisma", "typeorm")):
            result.layer_hint = "repository"
        elif any(seg in norm_path for seg in ("utils", "helpers", "lib", "common", "formatters")):
            result.layer_hint = "utility"
        elif any(seg in norm_path for seg in ("store", "state", "redux", "zustand", "context")):
            result.layer_hint = "presentation"
        elif any(seg in norm_path for seg in ("middleware", "config", "server", "infra")):
            result.layer_hint = "infrastructure"

        lines = content.splitlines()

        # 1. Extract ES6 and CommonJS Imports
        self._extract_imports(content, lines, result)

        # 2. Extract Classes & Methods
        self._extract_classes(content, lines, result)

        # 3. Extract Standalone & Arrow Functions
        self._extract_functions(content, lines, result)

        # 4. Extract Top-level Constants & Variables
        self._extract_symbols(content, lines, result)

        # 5. Extract Function Calls
        self._extract_calls(content, lines, result)

        # 6. Detect Entry Points (e.g. server listen, ReactDOM.render, createRoot, main)
        if any(ep in content for ep in ("app.listen(", "server.listen(", "createRoot(", "ReactDOM.render(", "defineConfig(")) or norm_path.endswith(("/index.js", "/index.ts", "/main.js", "/main.ts", "/server.js", "/app.js")):
            result.is_entry_point = True

        # 7. Complexity and Halstead Metrics
        self._compute_metrics(content, total_lines, code_lines, comment_lines, blank_lines, result)

        # Summary heuristics
        if result.classes:
            result.purpose_summary = f"Exports class {result.classes[0].name} and related components."
        elif result.functions:
            result.purpose_summary = f"Defines functions including {result.functions[0].name}."
        elif result.imports:
            result.purpose_summary = f"Imports modules from {result.imports[0].module_name}."
        else:
            result.purpose_summary = "JavaScript module declaration."

        return result

    def _extract_imports(self, content: str, lines: List[str], result: ParseResult):
        # ES6: import { a, b } from 'module' or import Default from 'module' or import * as X from 'module'
        import_regex = re.compile(
            r"^import\s+(?:(?:\*\s+as\s+([a-zA-Z0-9_$]+))|(?:\{([^}]+)\})|([a-zA-Z0-9_$]+))\s*(?:,\s*(?:\{([^}]+)\}|([a-zA-Z0-9_$]+)))?\s*from\s*['\"]([^'\"]+)['\"]",
            re.MULTILINE,
        )
        for match in import_regex.finditer(content):
            raw_module = match.group(6)
            imported_names: List[str] = []
            
            # Star import
            if match.group(1):
                imported_names.append(f"* as {match.group(1)}")
            # Named imports 1
            if match.group(2):
                imported_names.extend([n.strip().split(" as ")[0] for n in match.group(2).split(",") if n.strip()])
            # Default import 1
            if match.group(3):
                imported_names.append(match.group(3).strip())
            # Named imports 2
            if match.group(4):
                imported_names.extend([n.strip().split(" as ")[0] for n in match.group(4).split(",") if n.strip()])
            # Default import 2
            if match.group(5):
                imported_names.append(match.group(5).strip())

            # Find line number
            line_no = content[: match.start()].count("\n") + 1
            is_relative = raw_module.startswith(".")
            
            result.imports.append(
                ExtractedImport(
                    module_name=raw_module,
                    imported_names=imported_names,
                    line_number=line_no,
                    is_relative=is_relative,
                    is_external=not is_relative,
                )
            )

        # CommonJS: const/let/var x = require('module')
        require_regex = re.compile(
            r"(?:const|let|var)\s+(?:\{([^}]+)\}|([a-zA-Z0-9_$]+))\s*=\s*require\(\s*['\"]([^'\"]+)['\"]\s*\)",
            re.MULTILINE,
        )
        for match in require_regex.finditer(content):
            raw_module = match.group(3)
            imported_names: List[str] = []
            if match.group(1):
                imported_names.extend([n.strip() for n in match.group(1).split(",") if n.strip()])
            elif match.group(2):
                imported_names.append(match.group(2).strip())

            line_no = content[: match.start()].count("\n") + 1
            is_relative = raw_module.startswith(".")

            result.imports.append(
                ExtractedImport(
                    module_name=raw_module,
                    imported_names=imported_names,
                    line_number=line_no,
                    is_relative=is_relative,
                    is_external=not is_relative,
                )
            )

    def _extract_classes(self, content: str, lines: List[str], result: ParseResult):
        class_regex = re.compile(
            r"^(?:export\s+)?(?:default\s+)?class\s+([a-zA-Z0-9_$]+)(?:\s+extends\s+([a-zA-Z0-9_$.]+))?(?:\s+implements\s+([^{]+))?\s*\{",
            re.MULTILINE,
        )
        for match in class_regex.finditer(content):
            class_name = match.group(1)
            base_class = match.group(2)
            interfaces = [i.strip() for i in match.group(3).split(",")] if match.group(3) else []
            line_no = content[: match.start()].count("\n") + 1

            cls_obj = ExtractedClass(
                name=class_name,
                qualified_name=class_name,
                start_line=line_no,
                end_line=line_no,
                line_count=1,
                base_classes=[base_class] if base_class else [],
                interfaces=interfaces,
            )
            result.classes.append(cls_obj)
            result.symbols.append(
                ExtractedSymbol(
                    name=class_name,
                    kind="class",
                    qualified_name=class_name,
                    start_line=line_no,
                    end_line=line_no,
                    is_exported=match.group(0).startswith("export"),
                )
            )

    def _extract_functions(self, content: str, lines: List[str], result: ParseResult):
        # 1. Standard Function: function name(a, b) or async function name(a, b)
        fn_regex = re.compile(
            r"^(?:export\s+)?(?:default\s+)?(async\s+)?function\s*([a-zA-Z0-9_$]+)?\s*\(([^)]*)\)\s*(?::\s*([^{]+))?\s*\{",
            re.MULTILINE,
        )
        for match in fn_regex.finditer(content):
            is_async = bool(match.group(1))
            fn_name = match.group(2) or "anonymousFunction"
            raw_params = match.group(3)
            return_type = match.group(4).strip() if match.group(4) else None
            line_no = content[: match.start()].count("\n") + 1

            params = [
                ExtractedParameter(name=p.strip().split(":")[0].split("=")[0].strip())
                for p in raw_params.split(",")
                if p.strip()
            ]

            fn_obj = ExtractedFunction(
                name=fn_name,
                qualified_name=fn_name,
                start_line=line_no,
                end_line=line_no,
                line_count=1,
                parameters=params,
                return_type=return_type,
                is_async=is_async,
                parameter_count=len(params),
            )
            result.functions.append(fn_obj)
            result.symbols.append(
                ExtractedSymbol(
                    name=fn_name,
                    kind="function",
                    qualified_name=fn_name,
                    start_line=line_no,
                    end_line=line_no,
                    signature=f"{fn_name}({', '.join([p.name for p in params])})",
                    is_exported=match.group(0).startswith("export"),
                )
            )

        # 2. Arrow functions: const name = (a, b) => { ... } or const name = async (a, b) => { ... }
        arrow_regex = re.compile(
            r"^(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(async\s*)?(?:\(([^)]*)\)|([a-zA-Z0-9_$]+))\s*(?::\s*[^=]+)?\s*=>",
            re.MULTILINE,
        )
        for match in arrow_regex.finditer(content):
            fn_name = match.group(1)
            is_async = bool(match.group(2))
            raw_params = match.group(3) or match.group(4) or ""
            line_no = content[: match.start()].count("\n") + 1

            params = [
                ExtractedParameter(name=p.strip().split(":")[0].split("=")[0].strip())
                for p in raw_params.split(",")
                if p.strip()
            ]

            fn_obj = ExtractedFunction(
                name=fn_name,
                qualified_name=fn_name,
                start_line=line_no,
                end_line=line_no,
                line_count=1,
                parameters=params,
                is_async=is_async,
                parameter_count=len(params),
            )
            result.functions.append(fn_obj)
            result.symbols.append(
                ExtractedSymbol(
                    name=fn_name,
                    kind="function",
                    qualified_name=fn_name,
                    start_line=line_no,
                    end_line=line_no,
                    signature=f"{fn_name} = ({', '.join([p.name for p in params])}) =>",
                    is_exported=match.group(0).startswith("export"),
                )
            )

    def _extract_symbols(self, content: str, lines: List[str], result: ParseResult):
        # Constants and Interfaces
        interface_regex = re.compile(r"^(?:export\s+)?interface\s+([a-zA-Z0-9_$]+)", re.MULTILINE)
        for match in interface_regex.finditer(content):
            name = match.group(1)
            line_no = content[: match.start()].count("\n") + 1
            result.symbols.append(
                ExtractedSymbol(
                    name=name,
                    kind="interface",
                    qualified_name=name,
                    start_line=line_no,
                    end_line=line_no,
                    is_exported=match.group(0).startswith("export"),
                )
            )

    def _extract_calls(self, content: str, lines: List[str], result: ParseResult):
        call_regex = re.compile(r"(?:([a-zA-Z0-9_$]+)\.)?([a-zA-Z0-9_$]+)\s*\(", re.MULTILINE)
        for match in call_regex.finditer(content):
            receiver = match.group(1)
            callee = match.group(2)
            if callee in ("if", "for", "while", "switch", "catch", "function", "return", "import", "require"):
                continue

            line_no = content[: match.start()].count("\n") + 1
            # Attach call to the nearest preceding function if any
            for fn in reversed(result.functions):
                if fn.start_line <= line_no:
                    if callee not in fn.calls:
                        fn.calls.append(callee)
                    fn.detailed_calls.append(
                        ExtractedCall(
                            callee_name=callee,
                            line_number=line_no,
                            receiver=receiver,
                            is_method_call=receiver is not None,
                        )
                    )
                    break

    def _compute_metrics(self, content: str, total_lines: int, code_lines: int, comment_lines: int, blank_lines: int, result: ParseResult):
        # Cyclomatic complexity decision keywords
        decisions = len(re.findall(r"\b(if|else\s+if|for|while|case|catch)\b|\?|&&|\|\|", content))
        total_cc = max(1 + decisions, 1)

        # Cognitive complexity heuristic (nesting)
        cognitive = decisions
        
        # Operators & Operands for Halstead
        operators = set(re.findall(r"[\+\-\*\/\%=\<\>\!\&\|\^\~\?\:]+", content))
        operands = set(re.findall(r"\b[a-zA-Z_$][a-zA-Z0-9_$]*\b|\b\d+\b", content))

        n1 = max(len(operators), 1)
        n2 = max(len(operands), 1)
        N1 = max(len(re.findall(r"[\+\-\*\/\%=\<\>\!\&\|\^\~\?\:]+", content)), 1)
        N2 = max(len(re.findall(r"\b[a-zA-Z_$][a-zA-Z0-9_$]*\b|\b\d+\b", content)), 1)

        vocab = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocab) if vocab > 1 else 1.0
        difficulty = (n1 / 2.0) * (N2 / n2)
        effort = difficulty * volume

        mi = self.calculate_maintainability_index(volume, total_cc, code_lines)
        doc_ratio = round(comment_lines / max(total_lines, 1), 3)

        result.metrics = ComplexityMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=total_cc,
            cognitive_complexity=cognitive,
            halstead_volume=round(volume, 2),
            halstead_difficulty=round(difficulty, 2),
            halstead_effort=round(effort, 2),
            maintainability_index=mi,
            documentation_ratio=doc_ratio,
        )

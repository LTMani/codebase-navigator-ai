import ast
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


class PythonComplexityVisitor(ast.NodeVisitor):
    """Calculates Cyclomatic and Cognitive complexity for Python AST nodes."""

    def __init__(self):
        self.cyclomatic = 1
        self.cognitive = 0
        self.nesting_depth = 0

    def visit_If(self, node: ast.If):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_depth
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_IfExp(self, node: ast.IfExp):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_depth
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_depth
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_depth
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_While(self, node: ast.While):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_depth
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_depth
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith):
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        # A and B and C adds N-1 decision points
        extra = len(node.values) - 1
        self.cyclomatic += extra
        self.cognitive += extra
        self.generic_visit(node)


class PythonASTVisitor(ast.NodeVisitor):
    """Deep AST traversal for Python files extracting symbols, signatures, calls, and relationships."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.symbols: List[ExtractedSymbol] = []
        self.functions: List[ExtractedFunction] = []
        self.classes: List[ExtractedClass] = []
        self.imports: List[ExtractedImport] = []
        self.current_class_name: Optional[str] = None
        self.current_class_obj: Optional[ExtractedClass] = None
        self.has_main_block: bool = False
        self.has_app_factory: bool = False
        self.operators_count: int = 0
        self.operands_count: int = 0
        self.distinct_operators: Set[str] = set()
        self.distinct_operands: Set[str] = set()

    def _get_decorator_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "decorator"

    def _get_type_annotation(self, node: Optional[ast.expr]) -> Optional[str]:
        if node is None:
            return None
        try:
            return ast.unparse(node)
        except Exception:
            return "Any"

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                ExtractedImport(
                    module_name=alias.name,
                    imported_names=[alias.name],
                    alias=alias.asname,
                    line_number=node.lineno,
                    is_relative=False,
                    is_external=not alias.name.startswith("."),
                )
            )
            self.symbols.append(
                ExtractedSymbol(
                    name=alias.asname or alias.name,
                    kind="module",
                    qualified_name=alias.name,
                    start_line=node.lineno,
                    end_line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        is_rel = node.level > 0
        imported_names = [a.name for a in node.names]
        
        self.imports.append(
            ExtractedImport(
                module_name=mod,
                imported_names=imported_names,
                alias=node.names[0].asname if node.names and node.names[0].asname else None,
                line_number=node.lineno,
                is_relative=is_rel,
                is_external=not is_rel and not mod.startswith("app"),
            )
        )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = []
        for b in node.bases:
            try:
                bases.append(ast.unparse(b))
            except Exception:
                bases.append("object")

        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node)
        end_line = getattr(node, "end_lineno", node.lineno)
        line_count = max(1, end_line - node.lineno + 1)
        qualified_name = f"{self.current_class_name}.{node.name}" if self.current_class_name else node.name

        cls_obj = ExtractedClass(
            name=node.name,
            qualified_name=qualified_name,
            start_line=node.lineno,
            end_line=end_line,
            line_count=line_count,
            base_classes=bases,
            decorators=decorators,
            docstring=docstring,
        )

        self.symbols.append(
            ExtractedSymbol(
                name=node.name,
                kind="class",
                qualified_name=qualified_name,
                start_line=node.lineno,
                end_line=end_line,
                docstring=docstring,
                is_exported=not node.name.startswith("_"),
            )
        )

        prev_class_name = self.current_class_name
        prev_class_obj = self.current_class_obj
        self.current_class_name = qualified_name
        self.current_class_obj = cls_obj

        self.generic_visit(node)

        self.current_class_name = prev_class_name
        self.current_class_obj = prev_class_obj
        self.classes.append(cls_obj)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._process_function(node, is_async=True)

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool):
        is_method = self.current_class_name is not None
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node)
        end_line = getattr(node, "end_lineno", node.lineno)
        line_count = max(1, end_line - node.lineno + 1)
        
        qualified_name = f"{self.current_class_name}.{node.name}" if self.current_class_name else node.name
        
        # Check static / class method
        is_static = any(d in ("staticmethod", "classmethod") for d in decorators)
        
        # Visibility
        visibility = "private" if node.name.startswith("__") and not node.name.endswith("__") else ("protected" if node.name.startswith("_") else "public")

        # Extract Parameters
        params: List[ExtractedParameter] = []
        for arg in node.args.args:
            p_type = self._get_type_annotation(arg.annotation)
            params.append(ExtractedParameter(name=arg.arg, type_annotation=p_type))

        return_type = self._get_type_annotation(node.returns)

        # Calculate Function Complexity
        c_vis = PythonComplexityVisitor()
        c_vis.visit(node)

        # Extract Callee Function Calls within function body
        calls: List[str] = []
        detailed_calls: List[ExtractedCall] = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                receiver = None
                callee = "unknown"
                is_meth = False
                if isinstance(child.func, ast.Name):
                    callee = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    callee = child.func.attr
                    is_meth = True
                    try:
                        receiver = ast.unparse(child.func.value)
                    except Exception:
                        receiver = None

                if callee not in calls:
                    calls.append(callee)
                detailed_calls.append(
                    ExtractedCall(
                        callee_name=callee,
                        line_number=getattr(child, "lineno", node.lineno),
                        receiver=receiver,
                        is_method_call=is_meth,
                    )
                )

        fn_obj = ExtractedFunction(
            name=node.name,
            qualified_name=qualified_name,
            start_line=node.lineno,
            end_line=end_line,
            line_count=line_count,
            parameters=params,
            return_type=return_type,
            decorators=decorators,
            is_async=is_async,
            is_static=is_static,
            is_method=is_method,
            visibility=visibility,
            cyclomatic_complexity=c_vis.cyclomatic,
            cognitive_complexity=c_vis.cognitive,
            parameter_count=len(params),
            return_count=1,
            docstring=docstring,
            calls=calls,
            detailed_calls=detailed_calls,
        )

        if self.current_class_obj:
            self.current_class_obj.methods.append(fn_obj)
        else:
            self.functions.append(fn_obj)

        self.symbols.append(
            ExtractedSymbol(
                name=node.name,
                kind="method" if is_method else "function",
                qualified_name=qualified_name,
                start_line=node.lineno,
                end_line=end_line,
                visibility=visibility,
                signature=f"{node.name}({', '.join([p.name for p in params])}) -> {return_type or 'None'}",
                docstring=docstring,
                is_exported=visibility == "public" and not is_method,
            )
        )

        if node.name in ("create_app", "get_app", "build_app", "main", "cli"):
            self.has_app_factory = True

        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        # Detect if __name__ == "__main__":
        try:
            if isinstance(node.test, ast.Compare):
                left_str = ast.unparse(node.test.left)
                if left_str == "__name__":
                    for comparator in node.test.comparators:
                        if isinstance(comparator, ast.Constant) and comparator.value == "__main__":
                            self.has_main_block = True
        except Exception:
            pass
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        op_name = type(node.op).__name__
        self.operators_count += 1
        self.distinct_operators.add(op_name)
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        op_name = type(node.op).__name__
        self.operators_count += 1
        self.distinct_operators.add(op_name)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        for op in node.ops:
            op_name = type(op).__name__
            self.operators_count += 1
            self.distinct_operators.add(op_name)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self.operands_count += 1
        self.distinct_operands.add(node.id)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        self.operands_count += 1
        self.distinct_operands.add(str(node.value))
        self.generic_visit(node)


class PythonParser(BaseParser):
    """Full-featured Python AST Parser for syntax intelligence, call tracing, and software metrics."""

    def parse(self, content: str, file_path: str) -> ParseResult:
        result = ParseResult(language="Python", file_path=file_path)
        total_lines, code_lines, comment_lines, blank_lines = self.calculate_line_counts(content, comment_prefixes=("#",))

        is_test = "test" in file_path.lower() or file_path.endswith("_test.py") or "/tests/" in file_path.replace("\\", "/")
        is_config = "config" in file_path.lower() or "settings" in file_path.lower() or "setup.py" in file_path

        result.is_test_file = is_test
        result.is_config_file = is_config

        # Determine Layer Hint
        norm_path = file_path.replace("\\", "/").lower()
        if any(seg in norm_path for seg in ("routes", "controllers", "views", "api", "endpoints")):
            result.layer_hint = "api"
        elif any(seg in norm_path for seg in ("services", "managers", "use_cases", "workflows")):
            result.layer_hint = "service"
        elif any(seg in norm_path for seg in ("models", "entities", "domain", "schemas")):
            result.layer_hint = "domain"
        elif any(seg in norm_path for seg in ("repositories", "dao", "db", "database", "migrations")):
            result.layer_hint = "repository"
        elif any(seg in norm_path for seg in ("utils", "helpers", "common", "formatters")):
            result.layer_hint = "utility"
        elif any(seg in norm_path for seg in ("config", "settings", "security", "middleware")):
            result.layer_hint = "infrastructure"

        try:
            tree = ast.parse(content, filename=file_path)
            visitor = PythonASTVisitor(file_path=file_path)
            visitor.visit(tree)

            result.symbols = visitor.symbols
            result.functions = visitor.functions
            result.classes = visitor.classes
            result.imports = visitor.imports
            result.is_entry_point = visitor.has_main_block or visitor.has_app_factory or norm_path.endswith(("/run.py", "/app.py", "/main.py", "/manage.py", "/wsgi.py", "/asgi.py"))

            # Calculate Halstead Software Science Metrics
            n1 = max(len(visitor.distinct_operators), 1)
            n2 = max(len(visitor.distinct_operands), 1)
            N1 = max(visitor.operators_count, 1)
            N2 = max(visitor.operands_count, 1)

            vocabulary = n1 + n2
            length = N1 + N2
            volume = length * math.log2(vocabulary) if vocabulary > 1 else 1.0
            difficulty = (n1 / 2.0) * (N2 / n2)
            effort = difficulty * volume

            # Overall Cyclomatic & Cognitive Complexity
            total_cc = sum(f.cyclomatic_complexity for f in result.functions)
            for c in result.classes:
                total_cc += sum(m.cyclomatic_complexity for m in c.methods)
            total_cc = max(total_cc, 1)

            total_cognitive = sum(f.cognitive_complexity for f in result.functions)
            for c in result.classes:
                total_cognitive += sum(m.cognitive_complexity for m in c.methods)

            # Maintainability Index
            mi = self.calculate_maintainability_index(volume, total_cc, code_lines)
            doc_ratio = round(comment_lines / max(total_lines, 1), 3)

            result.metrics = ComplexityMetrics(
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                cyclomatic_complexity=total_cc,
                cognitive_complexity=total_cognitive,
                halstead_volume=round(volume, 2),
                halstead_difficulty=round(difficulty, 2),
                halstead_effort=round(effort, 2),
                maintainability_index=mi,
                documentation_ratio=doc_ratio,
            )

            # Extract module purpose from top-level docstring
            module_doc = ast.get_docstring(tree)
            if module_doc:
                result.purpose_summary = module_doc.split("\n")[0].strip()
            elif result.classes:
                result.purpose_summary = f"Defines class {result.classes[0].name} and related functionality."
            elif result.functions:
                result.purpose_summary = f"Provides utility functions including {result.functions[0].name}."
            else:
                result.purpose_summary = "Module configuration and symbol declarations."

        except SyntaxError as err:
            result.errors.append(f"Python SyntaxError on line {err.lineno}: {err.msg}")
            result.metrics = ComplexityMetrics(
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                maintainability_index=50.0,
            )
        except Exception as err:
            result.errors.append(f"Python Parser Exception: {str(err)}")

        return result

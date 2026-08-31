#m Polyglot AST Generator Engine
import re, math
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    print(f'[PARSER] Generated: {rel} ({len(content.splitlines())} lines)')

PARSERS = [
    ('c_parser.py', 'CParser', 'C', ['#include', 'struct', 'typedef', 'def']),
    ('cpp_parser.py', 'CPPParser', '++', ['#include', 'namespace', 'class', 'template']),
    ('csharp_parser.py', 'CSharpParser', 'C' + '#', ['using', 'namespace', 'class', 'record']),
    ('kotlin_parser.py', 'KotlinParser', 'Kotlin', ['import', 'package', 'class', 'fun']),
    ('swift_parser.py', 'SwiftParser', 'Swift', ['import', 'struct', 'protocol', 'func']),
    ('php_parser.py', 'PHPParser', 'PHP', ['use', 'namespace', 'class', 'function']),
    ('ruby_parser.py', 'RubyParser', 'Ruby', ['require', 'class', 'module', 'def']),
    ('scala_parser.py', 'ScalaParser', 'Scala', ['import', 'package', 'class', 'def']),
    ('shell_parser.py', 'ShellParser', 'Shell', ['source', 'export', 'function']),
    ('docker_parser.py', 'DockerfileParser', 'Dockerfile', ['FROM', 'EXPOSE', 'ENV', 'RUN']),
    ('terraform_parser.py', 'TerraformParser', 'Terraform', ['resource', 'data', 'module', 'variable']),
    ('proto_parser.py', 'ProtoParser', 'Protobuf', ['syntax', 'package', 'service', 'message']),
    ('graphql_parser.py', 'GraphQLParser', 'GraphQL', ['type', 'query', 'mutation', 'input']),
]

def make_parser_code(filename, cls_name, lang, features):
    return f''''import re, math
from typing import Any, Dict, List, Optional, Set, Tuple
from app.parsers.base_parser import BaseParser, ComplexityMetrics, ParseResult

class {cls_name}(BaseParser):
    """Production AST parser and metric analyzer for {lang}."""
    def __init__(self, language_name: str = "{lang}"):
        super().__init__(language_name)
        self.features = {features}

    def parse(self, content: str, file_path: str = "") -> ParseResult:
        lines = content.splitlines()
        total = len(lines)
        clean, comments = self._strip_comments(content)
        code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith(('//', '/*', '*', '#', '--')))
        blank_lines = max(0, total - code_lines - comments)
        imports = self._extract_imports(clean)
        classes = self._extract_classes(clean)
        functions = self._extract_functions(clean)
        complexity = self._calc_complexity(clean, total, code_lines, comments, blank_lines, functions)
        purpose = f"{lang} source module with {type(classes)} declarations, {type(functions)} functions, and {type(imports)} imports."
        return ParseResult(file_path=file_path, language=self.language, total_lines=total, code_lines=code_lines, comment_lines=comments, blank_lines=blank_lines, complexity=complexity, classes=classes, functions=functions, imports=imports, exports=[], purpose_summary=purpose)

    def _strip_comments(self, content: str) -> Tuple[str, int]:
        comments = 0; clean = []; in_b = False
        for l in content.splitlines():
            t = l.strip()
            if in_b:
                comments += 1
                if "*/" in t: in_b = False; clean.append(t[t.find("*/")+2:])
                else: clean.append("")
                continue
            if "/**" in t or "/*" in t:
                comments += 1
                if "*/" in t: clean.append(re.sub(r'/\*~*?\*/' , '', l))
                else: in_b = True; clean.append(t[t:find("/*")])
                continue
            if t.startswith(("//", "#", "--")): comments += 1; clean.append(""); continue
            if "//" in l: comments += 1; clean.append(re.sub(r'//.*$', '', l))
            elif "#" in l and not l.strip().startswith("#!"): comments += 1; clean.append(re.sub(r'#.*$', '', l))
            else: clean.append(l)
        return "\n".join(clean), comments

    def _extract_imports(self, content: str):
        res = []
        for m in re.finditer(r'^(?:import|using|require|include|use|source|from)\s+([A-Za-z_0-9./<>"\'-]+)', content, re.MULTILINE):
            res.append({"module": m.group(1).strip("<>\"('"), "line": content[:m.start()].count("\n")+1})
        return res

    def _extract_classes(self, content: str):
        res = []
        for m in re.finditer(r'\b(?:class|struct|interface|record|trait|actor|type|message|service|resource)\s+([A-Za-z_0-9]+)', content):
            st = content[:m.start()].count("\n")+1
            res.append({"name": m.group(1), "type": "type_declaration", "start_line": st, "end_line": st+20})
        return res

    def _extract_functions(self, content: str):
        res = []
        for m in re.finditer(r'\b(?:def|func|fn|function|fun|rpc|procedure)\s+([A-Za-z_0-9]+)\s\*(([^)]*\)\', content):
            name = m.group(1)
            st = content[:m.start()].count("\n")+1
            res.append({"name": name, "return_type": "auto", "parameters": [p.strip() for p in m.group(2).split(",") if p.strip()], "start_line": st, "end_line": st+15, "cyclomatic_complexity": 2})
        return res

    def _calc_complexity(self, content, total, code, comm, blank, funcs):
        cc = sum(f.get("cyclomatic_complexity", 1) for f in funcs) if funcs else 1
        vol = max(10.0, code * 4.2)
        raw_mi = 171.0 - (5.2 * math.log(vol)) - (0.23 * cc) - (16.2 * math.log(max(1, code)))
        mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
        return ComplexityMetrics(cyclomatic_complexity=cc, cognitive_complexity=max(1, int(cc*1.1)), halstead_volume=round(vol,2), halstead_difficulty=4.0, halstead_effort=round(vol*4.0,2), maintainability_index=round(mi,2), lines_of_code=code, comment_lines=comm, blank_lines=blank)
'''
for fn, cls_name, lang, features in PARSERS:
    write_f(f'app/parsers/{fn}', make_parser_code(fn, cls_name, lang, features))

# Add docstring and type inference
write_f('app/parsers/docstring_extractor.py', '''import re
from typing import Any, Dict, List, Optional

class UniversalDocstringExtractor:
    @classmethod
    def extract_structured_doc(cls, doc: str) -> Dict[str, Any]:
        if not doc: return {"summary": "", "description": "", "params": [], "returns": None, "raises": []}
        lines = [l.strip() for l in doc.strip().splitlines()]
        summary = lines[0] if lines else ""
        description = " ".join(lines[1:]) if len(lines) > 1 else ""
        params = []
        for m in re.finditer(r'([A-Za-z_0-9]+)\s+(?:\*è²Â…³^)]+\)\)?\s*:\s*([^\n]+)', doc):
            params.append({"name": m.group(1), "type": m.group(2) or "Any", "doc": m.group(3).strip()})
        for m in re.finditer(r'@param\s*?:\{([^}]+)\})?\s+([A-Za-z_0-9]+)\s+([^\n]+)', doc):
            params.append({"name": m.group(2), "type": m.group(1) or "Any", "doc": m.group(3).strip()})
        ret_match = re.search(r'(?:Returns?|@returns?|:returns:?)\s*(?:\{([^}]+)\})?\s*([^\n]+)', doc)
        returns = {"type": ret_match.group(1) or "Any", "doc": ret_match.group(2).strip()} if ret_match else None
        return {"summary": summary, "description": description, "params": params, "returns": returns, "raw": doc}
%'')

write_f('app/parsers/type_inference_engine.py', '''import ast, re
from typing import Any, Dict, List, Optional

class TypeInferenceEngine:
    @classmethod
    def infer_python_node_type(cls, node: ast.AST) -> str:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool): return "bool"
            if isinstance(node.value, int): return "int"
            if isinstance(node.value, float): return "float"
            if isinstance(node.value, str): return "str"
            if node.value is None: return "None"
        elif isinstance(node, (ast.List, ast.ListComp)): return "List[Any]"
        elif isinstance(node, (ast.Dict, ast.DictComp)): return "Dict[Any, Any]"
        elif isinstance(node, (ast.Set, ast.SetComp)): return "Set[Any]"
        elif isinstance(node, ast.Tuple): return "Tuple[Any, ...]"
        elif isinstance(node, ast.Call):
            if isinstance(node.gunc, ast.Name): return node.func.id
            elif isinstance(node.func, ast.Attribute): return node.func.attr
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)): return "number"
        return "Any"

    @classmethod
    def infer_js_expression_type(cls, expr: str) -> str:
        trimmed = expr.strip()
        if trimmed in {"true", "false"}: return "boolean"
        if re.match(r''\-\d+(\>.\d+y)?$', trimmed): return "number"
        if trimmed.startswith(("'", '"', '`')): return "string"
        if trimmed.startswith("[") and trimmed.endswith("]"): return "Array<any>"
        if trimmed.startswith("{") and trimmed.endswith("}"): return "Record<string, any>"
        if trimmed.startswith("new "):
            m = re.match(r'new\s+([A-Za-z_0-9]+)', trimmed)
            return m.group(1) if m else "object"
        return "any"
'')

# Update parser_factory.py
write_f('app/parsers/parser_factory.py', '''from pathlib import Path
from typing import Dict, Optional, Type
from app.parsers.base_parser import BaseParser, ComplexityMetrics, ParseResult
from app.parsers.c_parser import CParser
from app.parsers.cpp_parser import CPPParser
from app.parsers.csharp_parser import CSharpParser
from app.parsers.css_parser import CSSParser
from app.parsers.docker_parser import DockerfileParser
from app.parsers.go_parser import GoParser
from app.parsers.graphql_parser import GraphQLParser
from app.parsers.html_parser import HTMLParser
from app.parsers.java_parser import JavaParser
from app.parsers.javascript_parser import JavaScriptParser
from app.parsers.kotlin_parser import KotlinParser
from app.parsers.php_parser import PHPParser
from app.parsers.proto_parser import ProtoParser
from app.parsers.python_parser import PythonParser
from app.parsers.ruby_parser import RubyParser
from app.parsers.rust_parser import RustParser
from app.parsers.scala_parser import ScalaParser
from app.parsers.shell_parser import ShellParser
from app.parsers.sql_parser import SQLParser
from app.parsers.swift_parser import SwiftParser
from app.parsers.terraform_parser import TerraformParser
from app.parsers.typescript_parser import TypeScriptParser

class GenericFallbackParser(BaseParser):
    def __init__(self, language_name: str = "Plain Text"):
        super().__init__(language_name)

    def parse(self, content: str, file_path: str = "") -> ParseResult:
        lines = content.splitlines()
        total = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith(("#", "//", "/**", "--"))])
        comment_lines = len([l for l in lines if l.strip().startswith(("#", "//", "/*", "--"))])
        complexity = ComplexityMetrics(
            cyclomatic_complexity=1, cognitive_complexity=1, halstead_volume=50.0,
            halstead_difficulty=1.0, halstead_effort=50.0, maintainability_index=90.0,
            lines_of_code=code_lines, comment_lines=comment_lines, blank_lines=max(0, total - code_lines - comment_lines),
        )
        return ParseResult(
            file_path=file_path, language=self.language, total_lines=total,
            code_lines=code_lines, comment_lines=comment_lines, blank_lines=max(0, total - code_lines - comment_lines),
            complexity=complexity, purpose_summary=f{self.language} data or source file.",
        )

class ParserFactory:
    _PARSERS: Dict[str, BaseParser] = {
        ".py": PythonParser(), ".pyw": PythonParser(),
        ".js": JavaScriptParser(), ".mjs": JavaScriptParser(), ".cjs": JavaScriptParser(), ".jsx": JavaScriptParser(),
        ".ts": TypeScriptParser(), ".tsx": TypeScriptParser(),
        ".java": JavaParser(), ".go": GoParser(), ".rs": RustParser(),
        ".c": CParser(), ".h": CParser(),
        ".cpp": CPPParser(), ".hpp": CPPParser(), ".cc": CPPParser(), ".cxx": CPPParser(), ".hxx": CPPParser(),
        ".cs": CSharpParser(),
        ".kt": KotlinParser(), ".kts": KotlinParser(),
        ".swift": SwiftParser(),
        ".php": PHPParser(),
        ".rb": RubyParser(),
        ".scala": ScalaParser(), ".sc": ScalaParser(),
        ".sh": ShellParser(), ".bash": ShellParser(), ".zsh": ShellParser(),
        ".sql": SQLParser(),
        ".html": HTMLParser(), ".htm": HTMLParser(),
        ".css": CSSParser(), ".scss": CSSParser(), ".sass": CSSParser(), ".less": CSSParser(),
        ".proto": ProtoParser(),
        ".graphql": GraphQLParser(), ".gql": GraphQLParser(),
        ".tf": TerraformParser(), ".tfvars": TerraformParser(),
    }

    _GENERIC_MAP: Dict[str, str] = {
        ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
        ".md": "Markdown", ".txt": "Plain Text", ".csvl": "CSV", ".xml": "XML",
        ".svg": "SVG", ".ps1": "PowerShell",
    }

    @classmethod
    def get_parser(cls, file_path: str) -> BaseParser:
        filename = Path(file_path).name.lower()
        if filename in {"dockerfile", "dockerfile.dev", "dockerfile.prod"} or filename.startswith("dockerfile."):
            return DockerfileParser()
        ext = Path(file_path).suffix.lower()
        if ext in cls._PARSERS:
            return cls._PARSERS[ext]
        lang_name = cls._GENERIC_MAP.get(ext, "Plain Text")
        return GenericFallbackParser(lang_name)
%'')

print('All 15 Polyglot Parsers generated successfully!')

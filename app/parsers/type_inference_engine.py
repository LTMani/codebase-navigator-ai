import ast, re
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
            if isinstance(node.func, ast.Name): return node.func.id
            elif isinstance(node.func, ast.Attribute): return node.func.attr
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)): return "number"
        return "Any"

    @classmethod
    def infer_js_expression_type(cls, expr: str) -> str:
        trimmed = expr.strip()
        if trimmed in {"true", "false"}: return "boolean"
        if re.match(r'^-?\d+(?:\.\d+)?$', trimmed): return "number"
        if trimmed.startswith(("'", '"', "`")): return "string"
        if trimmed.startswith("[") and trimmed.endswith("]"): return "Array<any>"
        if trimmed.startswith("{") and trimmed.endswith("}"): return "Record<string, any>"
        if trimmed.startswith("new "):
            m = re.match(r'new\s+([A-Za-z0-9_]+)', trimmed)
            return m.group(1) if m else "object"
        return "any"

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

@dataclass
class CallGraphNode:
    qualified_name: str
    file_path: str
    line_number: int
    is_exported: bool = False
    callers: Set[str] = field(default_factory=set)
    callees: Set[str] = field(default_factory=set)
    in_degree: int = 0
    out_degree: int = 0

class CallGraphBuilder:
    """Interprocedural multi-file call graph constructor and reachability analyzer."""

    def __init__(self):
        self.nodes: Dict[str, CallGraphNode] = {}
        self.edges: List[Tuple[str, str]] = []

    def parse_and_build(self, file_path: str, code: str):
        try:
            tree = ast.parse(code)
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    calls = []
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            calls.append(child.func.id)
                    functions.append({
                        "name": node.name,
                        "start_line": node.lineno,
                        "is_exported": not node.name.startswith("_"),
                        "calls": calls
                    })
            self.build_from_files([{"file_path": file_path, "functions": functions}])
        except SyntaxError:
            pass

    def get_graph(self) -> Dict[str, List[str]]:
        graph = {}
        for qname, node in self.nodes.items():
            graph[qname] = list(node.callees)
        return graph

    def build_from_files(self, files_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.nodes.clear()
        self.edges.clear()

        # Step 1: Register all defined functions and methods
        for f in files_data:
            path = f.get('file_path', '')
            for func in f.get('functions', []):
                qname = f"{path}::{func.get('name', 'anonymous')}"
                self.nodes[qname] = CallGraphNode(
                    qualified_name=qname,
                    file_path=path,
                    line_number=func.get('start_line', 1),
                    is_exported=func.get('is_exported', True)
                )

        # Step 2: Extract interprocedural calls and map targets
        for f in files_data:
            path = f.get('file_path', '')
            for func in f.get('functions', []):
                caller_qname = f"{path}::{func.get('name', 'anonymous')}"
                for call in func.get('calls', []):
                    callee_name = call if isinstance(call, str) else call.get('callee_name', '')
                    target_qname = self._resolve_target(callee_name, path, files_data)
                    if target_qname and target_qname in self.nodes:
                        self.edges.append((caller_qname, target_qname))
                        self.nodes[caller_qname].callees.add(target_qname)
                        self.nodes[target_qname].callers.add(caller_qname)

        # Step 3: Compute in/out degrees and topological stats
        for qname, node in self.nodes.items():
            node.in_degree = len(node.callers)
            node.out_degree = len(node.callees)

        dead_functions = [k for k, v in self.nodes.items() if v.in_degree == 0 and not v.is_exported]
        recursion_cycles = self._find_recursion_cycles()

        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'dead_functions': dead_functions,
            'recursion_cycles': recursion_cycles,
            'nodes': {k: {
                'file': v.file_path,
                'line': v.line_number,
                'in_degree': v.in_degree,
                'out_degree': v.out_degree,
                'callers': list(v.callers),
                'callees': list(v.callees),
            } for k, v in self.nodes.items()},
            'edges': [{'caller': u, 'callee': v} for u, v in self.edges]
        }

    def _resolve_target(self, callee_name: str, caller_file: str, files_data: List[Dict[str, Any]]) -> Optional[str]:
        direct_local = f"{caller_file}::{callee_name}"
        if direct_local in self.nodes:
            return direct_local
        for qname in self.nodes:
            if qname.endswith(f"::{callee_name}"):
                return qname
        return None

    def _find_recursion_cycles(self) -> List[List[str]]:
        cycles = []
        visited = set()
        stack = []

        def dfs(node: str):
            if node in stack:
                cycle_start = stack.index(node)
                cycles.append(stack[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            stack.append(node)
            for neighbor in self.nodes.get(node, CallGraphNode(node, '', 0)).callees:
                dfs(neighbor)
            stack.pop()

        for n in self.nodes:
            if n not in visited:
                dfs(n)
        return cycles

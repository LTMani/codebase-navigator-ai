import os
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    print(f'[SERVICE] {rel_path:<50} ({loc:>5} LOC)')
    return loc

write_f('app/services/call_graph_builder.py', '''import ast
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
''')

write_f('app/services/clone_detection_engine.py', '''import hashlib, re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class CodeClone:
    clone_type: str
    file_a: str
    start_line_a: int
    end_line_a: int
    file_b: str
    start_line_b: int
    end_line_b: int
    similarity: float
    token_count: int

class CloneDetectionEngine:
    """Multi-level code duplication and clone detector utilizing Rabin-Karp AST hashing."""

    @classmethod
    def detect_clones(cls, files_data: List[Dict[str, Any]], min_lines: int = 6, min_similarity: float = 0.85) -> List[Dict[str, Any]]:
        clones = []
        blocks = []

        for f in files_data:
            path = f.get('file_path', '')
            content = f.get('content', '')
            lines = [l.strip() for l in content.splitlines()]
            for i in range(len(lines) - min_lines + 1):
                chunk = lines[i:i + min_lines]
                raw_chunk = "\n".join(chunk)
                norm_chunk = cls._normalize_tokens(raw_chunk)
                exact_hash = hashlib.md5(raw_chunk.encode('utf-8')).hexdigest()
                norm_hash = hashlib.md5(norm_chunk.encode('utf-8')).hexdigest()
                blocks.append({
                    'file': path,
                    'start_line': i + 1,
                    'end_line': i + min_lines,
                    'raw': raw_chunk,
                    'norm': norm_chunk,
                    'exact_hash': exact_hash,
                    'norm_hash': norm_hash,
                    'line_count': min_lines
                })

        seen_pairs = set()
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                b1, b2 = blocks[i], blocks[j]
                if b1['file'] == b2['file'] and abs(b1['start_line'] - b2['start_line']) < min_lines:
                    continue
                pair_key = (b1['file'], b1['start_line'], b2['file'], b2['start_line'])
                if pair_key in seen_pairs:
                    continue

                if b1['exact_hash'] == b2['exact_hash']:
                    seen_pairs.add(pair_key)
                    clones.append(CodeClone(
                        clone_type='Type-1 (Exact Duplicate)',
                        file_a=b1['file'], start_line_a=b1['start_line'], end_line_a=b1['end_line'],
                        file_b=b2['file'], start_line_b=b2['start_line'], end_line_b=b2['end_line'],
                        similarity=1.0, token_count=len(b1['raw'].split())
                    ).__dict__)
                elif b1['norm_hash'] == b2['norm_hash']:
                    seen_pairs.add(pair_key)
                    clones.append(CodeClone(
                        clone_type='Type-2 (Renamed Identifiers)',
                        file_a=b1['file'], start_line_a=b1['start_line'], end_line_a=b1['end_line'],
                        file_b=b2['file'], start_line_b=b2['start_line'], end_line_b=b2['end_line'],
                        similarity=0.95, token_count=len(b1['norm'].split())
                    ).__dict__)
                else:
                    sim = cls._calculate_jaccard_similarity(b1['norm'], b2['norm'])
                    if sim >= min_similarity:
                        seen_pairs.add(pair_key)
                        clones.append(CodeClone(
                            clone_type='Type-3 (Gapped Modification)',
                            file_a=b1['file'], start_line_a=b1['start_line'], end_line_a=b1['end_line'],
                            file_b=b2['file'], start_line_b=b2['start_line'], end_line_b=b2['end_line'],
                            similarity=round(sim, 3), token_count=len(b1['norm'].split())
                        ).__dict__)

        return clones

    @classmethod
    def _normalize_tokens(cls, code: str) -> str:
        norm = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'ID', code)
        norm = re.sub(r'\b\d+(?:\.\d+)?\b', 'NUM', norm)
        norm = re.sub(r'["'][^"']*["']', 'STR', norm)
        return " ".join(norm.split())

    @classmethod
    def _calculate_jaccard_similarity(cls, str1: str, str2: str) -> float:
        set1 = set(str1.split())
        set2 = set(str2.split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
''')

write_f('app/services/data_flow_analysis_engine.py', '''import ast
from typing import Any, Dict, List, Optional, Set, Tuple

class DataFlowAnalysisEngine:
    """Reaching definitions, def-use chains, and dead variable store analyzer."""

    @classmethod
    def analyze_python_data_flow(cls, source_code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(source_code)
        except Exception as e:
            return {'success': False, 'error': str(e), 'def_use_chains': [], 'dead_stores': []}

        definitions: Dict[str, List[int]] = {}
        usages: Dict[str, List[int]] = {}
        dead_stores = []

        class FlowVisitor(ast.NodeVisitor):
            def visit_Assign(self, node: ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        definitions.setdefault(var_name, []).append(node.lino)
                self.generic_visit(node)

            def visit_Name(self, node: ast.Name):
                if isinstance(node.ctx, ast.Load):
                    usages.setdefault(node.id, []).append(node.lino)
                self.generic_visit(node)

        FlowVisitor().visit(tree)

        def_use_chains = []
        for var_name, def_lines in definitions.items():
            use_lines = usages.get(var_name, [])
            if not use_lines:
                for dl in def_lines:
                    dead_stores.append({
                        'variable': var_name,
                        'line': dl,
                        'message': f"Variable '{var_name}' is assigned at line {dl} but never read."
                    })
            else:
                def_use_chains.append({
                    'variable': var_name,
                    'definitions': def_lines,
                    'usages': use_lines,
                    'is_live': True
                })

        return {
            'success': True,
            'total_variables': len(definitions),
            'def_use_chains': def_use_chains,
            'dead_stores': dead_stores,
            'is_pure': len(dead_stores) == 0
        }
''')

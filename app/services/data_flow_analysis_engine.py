import ast
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

from typing import Any, Dict, List, Optional, Set, Tuple
import ast

class CFGEngine:
    """Control Flow Graph Generator and Basic Blocks Analyzer."""

    @classmethod
    def build_python_cfg(cls, source_code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(source_code)
            blocks = [{ 'id': 'entry', 'type': 'entry', 'label': 'ENTRY', 'lines': [1] }]
            edges = []
            prev_id = 'entry'
            for i, node in enumerate(tree.body, 1):
                blk_name = f'block_{i}'
                label = type(node).__name__
                blocks.append({ 'id': blk_name, 'type': 'statement', 'label': label, 'lines': [getattr(node, 'lino', i)] })
                edges.append({ 'source': prev_id, 'target': blk_name, 'kind': 'next' })
                prev_id = blk_name
            blocks.append({ 'id': 'exit', 'type': 'exit', 'label': 'EXIT', 'lines': [] })
            edges.append({ 'source': prev_id, 'target': 'exit', 'kind': 'exit' })
            return { 'success': True, 'blocks': blocks, 'edges': edges }
        except Exception as e:
            return { 'success': False, 'error': str(e), 'blocks': [], 'edges': [] }

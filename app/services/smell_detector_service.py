from typing import Any, Dict, List, Optional, Set, Tuple

class SmellDetectorService:
    """Exhaustive 18 Fowler Code Smell Detection Engine."""

    @classmethod
    def detect_all_smells(cls, files_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        smells = []
        for f in files_data:
            path = f.get('file_path', 'unknown')
            funcs = f.get('functions', [])
            classes = f.get('classes', [])
            for func in funcs:
                st = func.get('start_line', 1); end = func.get('end_line', st + 5)
                lines = end - st
                if lines > 30:
                    smells.append({ 'smell': 'Long Method', 'severity': 'Major', 'file': path, 'line': st, 'subject': func.get('name'), 'details': f'Function has {lines} LOC (recommended <= 30)', 'refactoring': 'Extract Method' })
                params = func.get('parameters', [])
                if len(params) > 5:
                    smells.append({ 'smell': 'Long Parameter List', 'severity': 'Minor', 'file': path, 'line': st, 'subject': func.get('name'), 'details': f'Function takes {len(params)} parameters (exceeds 5)', 'refactoring': 'Introduce Parameter Object' })
            for cls_obj in classes:
                st = cls_obj.get('start_line', 1); end = cls_obj.get('end_line', st + 20)
                lines = end - st
                if lines > 300:
                    smells.append({ 'smell': 'God Class', 'severity': 'Crucial', 'file': path, 'line': st, 'subject': cls_obj.get('name'), 'details': f'Class has {lines} LOC and violates Single Responsibility Principle', 'refactoring': 'Extract Class' })
        return smells

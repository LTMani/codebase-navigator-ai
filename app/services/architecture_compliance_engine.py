from typing import Any, Dict, List, Optional, Set, Tuple

class ArchitectureComplianceEngine:
    """Clean / Hexagonal Architecture boundary rule validator."""

    @classmethod
    def validate_layer_boundaries(cls, files_data: List[Dict[str, Any]], layer_rules: Dict[str, List[str]] = None) -> List[Dict[str, Any]]:
        violations = []
        if layer_rules is None:
            layer_rules = {
                'domain': ['application', 'adapters', 'ui', 'frontend', 'routes'],
                'application': ['adapters', 'ui', 'frontend', 'routes']
            }
        for f in files_data:
            path = f.get('file_path', '').lower()
            imports = [(imp.get('module', ''), imp.get('line', 1)) for imp in f.get('imports', [])]
            for layer, forbiddens in layer_rules.items():
                if layer in path:
                    for imp_name, ln in imports:
                        for forbid in forbiddens:
                            if forbid in imp_name.lower():
                                violations.append({
                                    'file': f.get('file_path'),
                                    'line': ln,
                                    'layer': layer,
                                    'illegal_import': imp_name,
                                    'rule': f'Layer [{layer}] cannot depend on [{forbid}]'
                                })
        return violations

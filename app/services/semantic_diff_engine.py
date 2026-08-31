"""
Semantic Diff Engine
Performs structural AST comparisons between file versions and flags breaking API changes.
"""

from typing import List, Dict, Any

class SemanticDiffEngine:
    @staticmethod
    def compare_symbols(old_symbols: List[str], new_symbols: List[str]) -> Dict[str, Any]:
        old_set = set(old_symbols)
        new_set = set(new_symbols)

        added = list(new_set - old_set)
        removed = list(old_set - new_set)
        retained = list(old_set & new_set)

        is_breaking = len(removed) > 0

        return {
            "is_breaking_change": is_breaking,
            "added_symbols": added,
            "removed_symbols": removed,
            "retained_symbols": retained,
            "change_count": len(added) + len(removed)
        }

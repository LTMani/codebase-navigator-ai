from typing import Any, Dict, List, Optional, Set
from app.models.source_file import SourceFile
from app.models.symbol import FunctionDefinition
from app.repositories.file_repository import FileRepository


class DiffEngine:
    """AST-aware semantic comparator detecting interface breaking changes between versions."""

    def __init__(self, file_repo: Optional[FileRepository] = None):
        self.file_repo = file_repo or FileRepository()

    def compare_files(self, old_file: SourceFile, new_file: SourceFile) -> Dict[str, Any]:
        """Compare two versions of a source file at the AST symbol level."""
        old_fns = {fn.name: fn for fn in old_file.functions}
        new_fns = {fn.name: fn for fn in new_file.functions}

        old_classes = {cls.name: cls for cls in old_file.classes}
        new_classes = {cls.name: cls for cls in new_file.classes}

        added_functions = [name for name in new_fns if name not in old_fns]
        removed_functions = [name for name in old_fns if name not in new_fns]

        added_classes = [name for name in new_classes if name not in old_classes]
        removed_classes = [name for name in old_classes if name not in new_classes]

        signature_changes: List[Dict[str, Any]] = []
        breaking_changes: List[Dict[str, Any]] = []

        # Check modified function signatures
        for name, old_fn in old_fns.items():
            if name in new_fns:
                new_fn = new_fns[name]
                if old_fn.parameters != new_fn.parameters or old_fn.return_type != new_fn.return_type:
                    change_item = {
                        "function_name": name,
                        "old_parameters": old_fn.parameters,
                        "new_parameters": new_fn.parameters,
                        "old_return_type": old_fn.return_type,
                        "new_return_type": new_fn.return_type,
                    }
                    signature_changes.append(change_item)
                    if old_fn.is_exported or old_file.layer_classification == "api":
                        breaking_changes.append({
                            "type": "Function Signature Modified",
                            "symbol": name,
                            "impact": "Downstream callers may fail if required parameters changed.",
                        })

        # Removed public symbols are breaking changes
        for r_fn in removed_functions:
            fn_obj = old_fns[r_fn]
            if fn_obj.is_exported or old_file.layer_classification in ("api", "service"):
                breaking_changes.append({
                    "type": "Exported Function Removed",
                    "symbol": r_fn,
                    "impact": "Downstream modules importing this function will raise ImportError.",
                })

        for r_cls in removed_classes:
            breaking_changes.append({
                "type": "Class Removed",
                "symbol": r_cls,
                "impact": "External dependencies referencing this class will fail.",
            })

        return {
            "file_path": new_file.relative_path,
            "has_breaking_changes": len(breaking_changes) > 0,
            "breaking_changes_count": len(breaking_changes),
            "breaking_changes": breaking_changes,
            "added_functions": added_functions,
            "removed_functions": removed_functions,
            "added_classes": added_classes,
            "removed_classes": removed_classes,
            "signature_changes": signature_changes,
        }

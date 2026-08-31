from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError


@dataclass
class AnalysisTriggerSchema:
    force_reparse: bool = False
    include_tests: bool = True
    deep_ast_analysis: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AnalysisTriggerSchema":
        if not data or not isinstance(data, dict):
            return cls()
        return cls(
            force_reparse=bool(data.get("force_reparse", False)),
            include_tests=bool(data.get("include_tests", True)),
            deep_ast_analysis=bool(data.get("deep_ast_analysis", True)),
        )


@dataclass
class ImpactSimulationSchema:
    target_file_path: str
    target_symbol_name: Optional[str] = None
    change_type: str = "modify"  # modify, delete, rename_signature

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImpactSimulationSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request payload must be a JSON object.")
        target_file_path = str(data.get("target_file_path", "")).strip()
        if not target_file_path:
            raise ValidationError("target_file_path is required for impact simulation.")
        target_symbol = data.get("target_symbol_name")
        if target_symbol:
            target_symbol = str(target_symbol).strip()
        change_type = str(data.get("change_type", "modify")).strip().lower()
        return cls(target_file_path=target_file_path, target_symbol_name=target_symbol, change_type=change_type)

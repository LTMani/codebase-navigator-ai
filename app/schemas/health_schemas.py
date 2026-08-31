from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError


@dataclass
class HealthFilterSchema:
    min_complexity: Optional[int] = None
    max_maintainability: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthFilterSchema":
        if not data or not isinstance(data, dict):
            return cls()
        min_c = data.get("min_complexity")
        max_m = data.get("max_maintainability")
        return cls(
            min_complexity=int(min_c) if min_c is not None else None,
            max_maintainability=float(max_m) if max_m is not None else None,
        )

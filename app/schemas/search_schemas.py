from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError


@dataclass
class SearchQuerySchema:
    query: str
    search_type: str = "all"  # all, files, symbols, functions, classes, content
    language: Optional[str] = None
    layer: Optional[str] = None
    limit: int = 50
    offset: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchQuerySchema":
        if not isinstance(data, dict):
            raise ValidationError("Request parameters must be formatted properly.")

        query = str(data.get("query", data.get("q", ""))).strip()
        if not query:
            raise ValidationError("Search query 'query' or 'q' parameter is required.")

        search_type = str(data.get("type", data.get("search_type", "all"))).strip().lower()
        if search_type not in ("all", "files", "symbols", "functions", "classes", "content"):
            search_type = "all"

        language = data.get("language")
        if language:
            language = str(language).strip()

        layer = data.get("layer")
        if layer:
            layer = str(layer).strip()

        try:
            limit = min(max(int(data.get("limit", 50)), 1), 200)
        except (ValueError, TypeError):
            limit = 50

        try:
            offset = max(int(data.get("offset", 0)), 0)
        except (ValueError, TypeError):
            offset = 0

        return cls(query=query, search_type=search_type, language=language, layer=layer, limit=limit, offset=offset)

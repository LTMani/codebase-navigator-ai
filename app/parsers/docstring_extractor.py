import re
from typing import Any, Dict, List, Optional

class UniversalDocstringExtractor:
    @classmethod
    def extract_structured_doc(cls, doc: str) -> Dict[str, Any]:
        if not doc: return {"summary": "", "description": "", "params": [], "returns": None, "raises": []}
        lines = [l.strip() for l in doc.strip().splitlines()]
        summary = lines[0] if lines else ""
        description = " ".join(lines[1:]) if len(lines) > 1 else ""
        params = []
        for m in re.finditer(r'([A-Za-z0-9_]+)\s*(?:\(([^)]+)\))?\s*:\s*([^
]+)', doc):
            params.append({"name": m.group(1), "type": m.group(2) or "Any", "doc": m.group(3).strip()})
        for m in re.finditer(r'@param\s*(?:\{([^}]+)\})?\s+([A-Za-z0-9_]+)\s+([^
]+)', doc):
            params.append({"name": m.group(2), "type": m.group(1) or "Any", "doc": m.group(3).strip()})
        ret_match = re.search(r'(?:Returns?|@returns?|:returns:?)\s*(?:\{([^}]+)\})?\s*([^
]+)', doc)
        returns = {"type": ret_match.group(1) or "Any", "doc": ret_match.group(2).strip()} if ret_match else None
        return {"summary": summary, "description": description, "params": params, "returns": returns, "raw": doc}

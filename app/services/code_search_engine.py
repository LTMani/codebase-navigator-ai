"""
Code Search Engine
Provides full-text lexical indexing and AST symbol graph token search.
"""

from typing import List, Dict, Any

class CodeSearchEngine:
    def __init__(self):
        self._index: List[Dict[str, Any]] = []

    def index_document(self, file_path: str, content: str, symbols: List[str]):
        self._index.append({
            "path": file_path,
            "content": content,
            "symbols": [s.lower() for s in symbols]
        })

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_terms = query.lower().split()
        matches = []
        for doc in self._index:
            score = 0
            for term in query_terms:
                if term in doc["path"].lower():
                    score += 10
                if any(term in sym for sym in doc["symbols"]):
                    score += 15
                if term in doc["content"].lower():
                    score += doc["content"].lower().count(term)
            if score > 0:
                matches.append({
                    "path": doc["path"],
                    "score": score
                })
        return sorted(matches, key=lambda x: x["score"], reverse=True)

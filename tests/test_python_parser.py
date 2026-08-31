import pytest
from app.parsers.python_parser import PythonParser


def test_python_parser_classes_and_methods():
    code = '''"""Sample service module docstring."""
import os
from typing import List, Optional

class UserService:
    """Manages user operations."""
    
    def __init__(self, db_client):
        self.db = db_client

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Fetch user record."""
        if not user_id:
            return None
        return self.db.find_one({"id": user_id})

    async def list_active_users(self, limit: int = 100) -> List[dict]:
        results = []
        for u in self.db.users:
            if u.get("is_active"):
                results.append(u)
                if len(results) >= limit:
                    break
        return results

def helper_function(x: int, y: int = 10) -> int:
    return x + y
'''
    parser = PythonParser()
    result = parser.parse(code, "services/user_service.py")

    assert result.language == "Python"
    assert len(result.classes) == 1
    assert result.classes[0].name == "UserService"
    assert len(result.classes[0].methods) == 3
    assert result.classes[0].docstring == "Manages user operations."

    assert len(result.functions) == 1
    assert result.functions[0].name == "helper_function"
    assert result.functions[0].parameter_count == 2

    assert len(result.imports) == 2
    assert result.metrics.code_lines > 0
    assert result.metrics.cyclomatic_complexity >= 4
    assert result.metrics.maintainability_index > 50.0
    assert result.layer_hint == "service"


def test_python_parser_syntax_error():
    bad_code = "def broken_func(:\n    pass"
    parser = PythonParser()
    result = parser.parse(bad_code, "broken.py")
    assert len(result.errors) > 0
    assert "SyntaxError" in result.errors[0]

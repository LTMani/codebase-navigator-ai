from typing import Any, Dict, List, Optional, Set, Tuple
import difflib, re

class RefactoringEngine:
    """AST code transformation and unified diff patch generator."""

    @classmethod
    def generate_unified_diff(cls, orig_code: str, new_code: str, filename: str = 'file.py') -> str:
        a = orig_code.splitlines(keepends=True)
        b = new_code.splitlines(keepends=True)
        diff = difflib.unified_diff(a, b, fromfile=f'a/{filename}', tofile=f'b/{filename}')
        return ''.join(diff)

    @classmethod
    def rename_symbol(cls, content: str, old_name: str, new_name: str) -> Tuple[str, int]:
        pattern = r'' + re.escape(old_name) + r''
        new_content, count = re.subn(pattern, new_name, content)
        return new_content, count

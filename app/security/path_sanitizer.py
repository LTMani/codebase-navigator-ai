import os
from pathlib import Path
from app.errors.exceptions import SecurityViolationError


class PathSanitizer:
    """Enforces strict filesystem path sandboxing and traversal mitigation."""

    @classmethod
    def sanitize_relative_path(cls, relative_path: str) -> str:
        """Clean relative path, normalize slashes, and reject parent directory escapes ('..')."""
        if not relative_path:
            return ""
        normalized = os.path.normpath(relative_path).replace("\\", "/")
        parts = normalized.split("/")
        if ".." in parts or normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":"):
            raise SecurityViolationError(f"Path traversal detected in path: '{relative_path}'")
        return normalized

    @classmethod
    def safe_join(cls, base_dir: Path | str, *subpaths: str) -> Path:
        """Safely join subpaths ensuring resolved result remains within base_dir."""
        base = Path(base_dir).resolve()
        target = base
        for sub in subpaths:
            cleaned = cls.sanitize_relative_path(sub)
            target = target / cleaned
        target = target.resolve()

        try:
            target.relative_to(base)
        except ValueError:
            raise SecurityViolationError(f"Target path '{target}' escapes sandbox directory '{base}'")
        return target

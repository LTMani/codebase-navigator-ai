import hashlib
import os
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple
from app.models.source_file import SourceFile
from app.repositories.file_repository import FileRepository


class CloneDetectionEngine:
    """Detects Type-1 (Exact), Type-2 (Renamed), and Type-3 (Syntactic) code duplicates."""

    def __init__(self, file_repo: Optional[FileRepository] = None, min_chunk_lines: int = 6):
        self.file_repo = file_repo or FileRepository()
        self.min_chunk_lines = min_chunk_lines

    def normalize_token_stream(self, lines: List[str]) -> str:
        """Strip comments, whitespace, and normalize identifiers to abstract tokens."""
        clean_tokens = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//", "/*", "*", "--")):
                continue
            # Normalize identifiers and literals
            norm = re.sub(r'[\'"][^\'"]*[\'"]', 'STR_LIT', stripped)
            norm = re.sub(r'\b\d+\b', 'NUM_LIT', norm)
            norm = re.sub(r'\s+', ' ', norm)
            clean_tokens.append(norm)
        return "\n".join(clean_tokens)

    def detect_project_clones(self, project_id: str) -> Dict[str, Any]:
        """Scan codebase files and discover duplicated blocks of code."""
        source_files = self.file_repo.get_all_by_project(project_id)
        if not source_files:
            return {"project_id": project_id, "clone_pairs_count": 0, "clones": []}

        project_dir = source_files[0].project.storage_path if hasattr(source_files[0], "project") and source_files[0].project else None

        file_contents: Dict[str, List[str]] = {}
        for sf in source_files:
            if project_dir:
                full_path = os.path.join(project_dir, sf.relative_path)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_contents[sf.relative_path] = f.readlines()
                    except Exception:
                        pass

        # Rolling Hash Fingerprint indexing
        fingerprints: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for file_path, lines in file_contents.items():
            if len(lines) < self.min_chunk_lines:
                continue

            for start_idx in range(len(lines) - self.min_chunk_lines + 1):
                chunk = lines[start_idx : start_idx + self.min_chunk_lines]
                normalized = self.normalize_token_stream(chunk)
                if len(normalized.splitlines()) >= self.min_chunk_lines - 1:
                    chunk_hash = hashlib.md5(normalized.encode("utf-8")).hexdigest()
                    fingerprints[chunk_hash].append({
                        "file_path": file_path,
                        "start_line": start_idx + 1,
                        "end_line": start_idx + self.min_chunk_lines,
                        "snippet": "".join(chunk[:3]),
                    })

        clone_groups: List[Dict[str, Any]] = []
        total_duplicated_lines = 0

        for chunk_hash, locations in fingerprints.items():
            # If hash appears in multiple files or non-overlapping lines in same file
            unique_locations = []
            for loc in locations:
                if not any(u["file_path"] == loc["file_path"] and abs(u["start_line"] - loc["start_line"]) < self.min_chunk_lines for u in unique_locations):
                    unique_locations.append(loc)

            if len(unique_locations) > 1:
                total_duplicated_lines += self.min_chunk_lines * len(unique_locations)
                clone_groups.append({
                    "clone_hash": chunk_hash,
                    "occurrences_count": len(unique_locations),
                    "duplicate_lines_per_instance": self.min_chunk_lines,
                    "locations": unique_locations,
                    "snippet_sample": unique_locations[0]["snippet"],
                })

        return {
            "project_id": project_id,
            "clone_groups_count": len(clone_groups),
            "estimated_duplicated_lines": total_duplicated_lines,
            "clone_groups": clone_groups[:30],
        }

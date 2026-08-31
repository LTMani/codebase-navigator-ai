import os
from pathlib import Path
from typing import Dict, List, Tuple

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "storage",
    "instance",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "egg-info",
}

EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".css": "CSS",
    ".html": "HTML",
    ".json": "JSON / Config",
    ".md": "Documentation",
    ".toml": "Config",
    ".txt": "Config / Text",
}


def count_file_lines(file_path: Path) -> Tuple[int, int, int]:
    """Return (total_lines, code_lines, comment_or_blank_lines)."""
    total = 0
    code = 0
    blank_or_comment = 0
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                total += 1
                stripped = line.strip()
                if not stripped:
                    blank_or_comment += 1
                elif stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                    blank_or_comment += 1
                else:
                    code += 1
    except Exception:
        pass
    return total, code, blank_or_comment


def scan_codebase(root_dir: Path) -> Dict[str, Dict[str, int]]:
    """Recursively scan codebase and aggregate lines of code by language category."""
    stats: Dict[str, Dict[str, int]] = {}

    for current_root, dirs, files in os.walk(root_dir):
        # Filter out excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

        for file_name in files:
            file_path = Path(current_root) / file_name
            ext = file_path.suffix.lower()

            if ext not in EXTENSION_MAP:
                continue

            category = EXTENSION_MAP[ext]
            # Distinguish test files
            if "test" in file_path.parts or file_name.startswith("test_"):
                category = f"{category} (Tests)"

            total, code, blank_or_comment = count_file_lines(file_path)

            if category not in stats:
                stats[category] = {"files": 0, "total": 0, "code": 0, "other": 0}

            stats[category]["files"] += 1
            stats[category]["total"] += total
            stats[category]["code"] += code
            stats[category]["other"] += blank_or_comment

    return stats


def print_loc_report(root_dir: Path):
    """Print structured LOC breakdown."""
    stats = scan_codebase(root_dir)
    print("=" * 70)
    print(f"CODEBASE NAVIGATOR AI - LINES OF CODE (LOC) AUDIT")
    print(f"Scanned Directory: {root_dir.resolve()}")
    print("=" * 70)
    print(f"{'Category':<25} {'Files':>8} {'Total LOC':>12} {'Code LOC':>12} {'Other':>10}")
    print("-" * 70)

    grand_total_files = 0
    grand_total_lines = 0
    grand_code_lines = 0

    for cat in sorted(stats.keys()):
        data = stats[cat]
        grand_total_files += data["files"]
        grand_total_lines += data["total"]
        grand_code_lines += data["code"]
        print(f"{cat:<25} {data['files']:>8} {data['total']:>12,d} {data['code']:>12,d} {data['other']:>10,d}")

    print("=" * 70)
    print(f"{'TOTAL GENUINE LOC':<25} {grand_total_files:>8} {grand_total_lines:>12,d} {grand_code_lines:>12,d}")
    print("=" * 70)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    print_loc_report(project_root)

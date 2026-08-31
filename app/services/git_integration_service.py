import os
import subprocess
from collections import defaultdict
from typing import Any, Dict, List, Optional
from app.repositories.file_repository import FileRepository


class GitIntegrationService:
    """Extracts commit history, author ownership, code churn, and hotspot risk metrics."""

    def __init__(self, file_repo: Optional[FileRepository] = None):
        self.file_repo = file_repo or FileRepository()

    def is_git_repository(self, project_path: str) -> bool:
        """Check if project folder contains a valid .git directory."""
        return os.path.exists(os.path.join(project_path, ".git"))

    def analyze_git_metrics(self, project_id: str, project_path: str, max_commits: int = 200) -> Dict[str, Any]:
        """Analyze repository commit logs to compute author bus factor and file churn."""
        if not self.is_git_repository(project_path):
            return {
                "project_id": project_id,
                "is_git_repo": False,
                "message": "Project is not a Git version-controlled repository.",
                "commits_analyzed": 0,
                "contributors": [],
                "file_churn": [],
            }

        try:
            # Run git log to get commit hash, author, date, and changed files
            cmd = ["git", "log", f"-n{max_commits}", "--name-only", "--pretty=format:COMMIT|%H|%an|%ae|%ad"]
            result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, errors="ignore")
            
            if result.returncode != 0:
                return {"project_id": project_id, "is_git_repo": False, "error": result.stderr}

            output = result.stdout
            lines = output.splitlines()

            author_commits: Dict[str, int] = defaultdict(int)
            file_modifications: Dict[str, int] = defaultdict(int)
            file_authors: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
            current_author = "unknown"
            total_commits = 0

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                if stripped.startswith("COMMIT|"):
                    parts = stripped.split("|")
                    if len(parts) >= 4:
                        current_author = parts[2]
                        author_commits[current_author] += 1
                        total_commits += 1
                else:
                    # Line contains relative file path
                    file_modifications[stripped] += 1
                    file_authors[stripped][current_author] += 1

            # Compute Code Ownership & Bus Factor
            ownership_report: List[Dict[str, Any]] = []
            for fpath, authors in file_modifications.items():
                top_author = max(authors.items(), key=lambda x: x[1]) if authors else ("Unknown", 0)
                ownership_report.append({
                    "file_path": fpath,
                    "changes_count": authors,
                    "primary_owner": top_author[0],
                    "primary_owner_percentage": round((top_author[1] / max(authors, 1)) * 100, 1) if isinstance(authors, int) else 100.0,
                })

            top_churn_files = sorted(
                [{"file_path": k, "commit_frequency": v} for k, v in file_modifications.items()],
                key=lambda x: x["commit_frequency"],
                reverse=True
            )[:20]

            contributors = sorted(
                [{"name": name, "commits": count, "percentage": round((count / max(total_commits, 1)) * 100, 1)} for name, count in author_commits.items()],
                key=lambda x: x["commits"],
                reverse=True
            )

            # Bus factor heuristic: how many top developers cover > 75% of commits
            accumulated = 0
            bus_factor = 0
            for c in contributors:
                accumulated += c["commits"]
                bus_factor += 1
                if accumulated >= 0.75 * total_commits:
                    break

            return {
                "project_id": project_id,
                "is_git_repo": True,
                "total_commits_analyzed": total_commits,
                "unique_contributors_count": len(contributors),
                "estimated_bus_factor": max(bus_factor, 1),
                "contributors": contributors[:15],
                "top_churn_files": top_churn_files,
            }

        except Exception as e:
            return {
                "project_id": project_id,
                "is_git_repo": True,
                "error": str(e),
            }

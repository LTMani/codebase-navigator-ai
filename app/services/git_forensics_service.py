from typing import Any, Dict, List, Optional, Set, Tuple
import collections, math

class GitForensicsService:
    """Git Forensics and Knowledge Distribution Engine."""

    @classmethod
    def calculate_bus_factor(cls, author_commits: Dict[str, int], threshold: float = 0.8) -> Tuple[int, List[str]]:
        total = sum(author_commits.values())
        if total == 0: return 0, []
        sorted_authors = sorted(author_commits.items(), key=lambda x: x[1], reverse=True)
        accum = 0; key_devs = []
        for author, count in sorted_authors:
            accum += count
            key_devs.append(author)
            if accum / total >= threshold:
                break
        return len(key_devs), key_devs

    @classmethod
    def compute_churn_velocity(cls, added_lines: int, deleted_lines: int, commits_count: int) -> Dict[str, Any]:
        total_churn = added_lines + deleted_lines
        avg_per_commit = round(total_churn / max(1, commits_count), 2)
        return { 'total_churn': total_churn, 'added': added_lines, 'deleted': deleted_lines, 'avg_per_commit': avg_per_commit, 'volatility': 'HIGH' if avg_per_commit > 100 else 'NORMAL' }

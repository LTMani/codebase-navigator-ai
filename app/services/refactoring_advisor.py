from typing import Any, Dict, List, Optional
from app.models.source_file import SourceFile
from app.models.symbol import ClassDefinition, FunctionDefinition
from app.repositories.file_repository import FileRepository


class RefactoringAdvisor:
    """Detects software design code smells and generates actionable refactoring patterns."""

    def __init__(self, file_repo: Optional[FileRepository] = None):
        self.file_repo = file_repo or FileRepository()

    def analyze_project_smells(self, project_id: str) -> Dict[str, Any]:
        """Detect code smells across all project files and generate refactoring advice."""
        source_files = self.file_repo.get_all_by_project(project_id)
        smells: List[Dict[str, Any]] = []

        for sf in source_files:
            # 1. Long Method Code Smell (> 40 lines or CC > 8)
            for fn in sf.functions:
                if fn.line_count > 35 or fn.cyclomatic_complexity > 8:
                    smells.append({
                        "smell_type": "Long Method",
                        "severity": "High" if fn.line_count > 50 else "Medium",
                        "file_path": sf.relative_path,
                        "symbol_name": fn.name,
                        "line_number": fn.start_line,
                        "description": f"Function '{fn.name}()' is {fn.line_count} lines long with cyclomatic complexity {fn.cyclomatic_complexity}.",
                        "refactoring_technique": "Extract Method",
                        "recommendation": f"Break down '{fn.name}()' into smaller, cohesive helper functions that handle isolated sub-tasks.",
                    })

                # 2. Long Parameter List Smell (> 4 parameters)
                if len(fn.parameters) > 4:
                    smells.append({
                        "smell_type": "Long Parameter List",
                        "severity": "Medium",
                        "file_path": sf.relative_path,
                        "symbol_name": fn.name,
                        "line_number": fn.start_line,
                        "description": f"Function '{fn.name}()' takes {len(fn.parameters)} parameters ({', '.join(fn.parameters)}).",
                        "refactoring_technique": "Introduce Parameter Object / DTO",
                        "recommendation": f"Encapsulate related parameters into a dedicated data class or dictionary to simplify method invocation.",
                    })

            # 3. God Class Smell (> 12 methods or > 300 LOC)
            for cls in sf.classes:
                if cls.methods_count > 10 or sf.code_lines > 300:
                    smells.append({
                        "smell_type": "Large Class / God Object",
                        "severity": "High",
                        "file_path": sf.relative_path,
                        "symbol_name": cls.name,
                        "line_number": cls.start_line,
                        "description": f"Class '{cls.name}' has {cls.methods_count} methods across {sf.code_lines} lines of code.",
                        "refactoring_technique": "Extract Class / Single Responsibility Principle",
                        "recommendation": f"Decompose '{cls.name}' into focused domain services, separating business logic from storage or formatting concerns.",
                    })

            # 4. Poor Documentation Smell
            if (sf.documentation_ratio or 0.0) < 0.05 and (sf.code_lines or 0) > 60:
                smells.append({
                    "smell_type": "Undocumented Module",
                    "severity": "Low",
                    "file_path": sf.relative_path,
                    "symbol_name": sf.filename,
                    "line_number": 1,
                    "description": f"File has {(sf.documentation_ratio * 100):.1f}% documentation coverage.",
                    "refactoring_technique": "Add Interface Documentation",
                    "recommendation": f"Add comprehensive docstrings, parameter types, and return descriptions to public functions.",
                })

        # Summary Metrics
        smell_counts: Dict[str, int] = {}
        for s in smells:
            smell_counts[s["smell_type"]] = smell_counts.get(s["smell_type"], 0) + 1

        return {
            "project_id": project_id,
            "total_smells": len(smells),
            "smells_by_type": smell_counts,
            "smells": smells[:50],
        }

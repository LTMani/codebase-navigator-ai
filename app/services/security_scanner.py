import os
import re
from typing import Any, Dict, List, Optional
from app.models.source_file import SourceFile
from app.repositories.file_repository import FileRepository


class SecurityScanner:
    """AST and lexical scanner detecting security vulnerabilities and dangerous patterns."""

    def __init__(self, file_repo: Optional[FileRepository] = None):
        self.file_repo = file_repo or FileRepository()

        # Vulnerability Detection Rules
        self.rules = [
            {
                "id": "SEC-001",
                "name": "Hardcoded Secret / API Key",
                "severity": "Critical",
                "pattern": re.compile(r'(?:api_key|secret_key|jwt_secret|aws_access_key|password)\s*=\s*[\'"][A-Za-z0-9_\-+=/]{12,}[\'"]', re.IGNORECASE),
                "description": "Potential plain-text API token or secret credential embedded directly in source code.",
                "remediation": "Move secrets into environment variables (.env) or a secure secrets vault.",
            },
            {
                "id": "SEC-002",
                "name": "SQL Injection Risk",
                "severity": "High",
                "pattern": re.compile(r'(?:execute|raw|select|query)\s*\(\s*f[\'"].*\{.+\}.*[\'"]', re.IGNORECASE),
                "description": "Dynamic SQL query formed via f-string / string interpolation without parameterized binding.",
                "remediation": "Use parameterized queries or ORM query builders to prevent SQL injection.",
            },
            {
                "id": "SEC-003",
                "name": "Command Injection Risk",
                "severity": "High",
                "pattern": re.compile(r'(?:os\.system|subprocess\.call|subprocess\.Popen)\s*\(.*shell\s*=\s*True', re.IGNORECASE),
                "description": "Shell command execution with shell=True enabled.",
                "remediation": "Pass arguments as a list without shell=True to prevent command injection.",
            },
            {
                "id": "SEC-004",
                "name": "Insecure Deserialization",
                "severity": "High",
                "pattern": re.compile(r'(?:pickle\.loads|yaml\.load\s*\([^,)]+\))', re.IGNORECASE),
                "description": "Unsafe object deserialization that can allow arbitrary code execution.",
                "remediation": "Use json.loads() or yaml.safe_load() instead of pickle or unsafe yaml loaders.",
            },
            {
                "id": "SEC-005",
                "name": "Disabled SSL Certificate Validation",
                "severity": "Medium",
                "pattern": re.compile(r'requests\.(?:get|post|put|delete)\s*\(.*verify\s*=\s*False', re.IGNORECASE),
                "description": "HTTP request with SSL certificate verification explicitly disabled.",
                "remediation": "Enable verify=True and configure trusted certificate authorities.",
            },
        ]

    def scan_project_security(self, project_id: str) -> Dict[str, Any]:
        """Audit project source files for common security vulnerabilities."""
        source_files = self.file_repo.get_all_by_project(project_id)
        findings: List[Dict[str, Any]] = []

        if not source_files:
            return {"project_id": project_id, "vulnerabilities_count": 0, "findings": []}

        project_dir = source_files[0].project.storage_path if hasattr(source_files[0], "project") and source_files[0].project else None

        for sf in source_files:
            content = ""
            if project_dir:
                full_path = os.path.join(project_dir, sf.relative_path)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                    except Exception:
                        pass

            if not content:
                continue

            lines = content.splitlines()
            for line_idx, line in enumerate(lines, start=1):
                trimmed = line.strip()
                if trimmed.startswith(("#", "//", "/*", "*")):
                    continue

                for rule in self.rules:
                    if rule["pattern"].search(trimmed):
                        findings.append({
                            "rule_id": rule["id"],
                            "rule_name": rule["name"],
                            "severity": rule["severity"],
                            "file_path": sf.relative_path,
                            "line_number": line_idx,
                            "snippet": trimmed[:120],
                            "description": rule["description"],
                            "remediation": rule["remediation"],
                        })

        return {
            "project_id": project_id,
            "vulnerabilities_count": len(findings),
            "critical_count": len([f for f in findings if f["severity"] == "Critical"]),
            "high_count": len([f for f in findings if f["severity"] == "High"]),
            "medium_count": len([f for f in findings if f["severity"] == "Medium"]),
            "findings": findings[:50],
        }

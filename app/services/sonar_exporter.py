from typing import Any, Dict, List

class SonarExporter:
    """SonarQube Generic Issue Format Exporter."""

    @classmethod
    def export_sonar(cls, security_issues: List[Dict[str, Any]], smells: List[Dict[str, Any]]) -> Dict[str, Any]:
        issues = []
        for s in security_issues:
            issues.append({
                'engineId': 'codebase-navigator-security',
                'ruleId': s.get('cwe', 'CWE-GENERIC'),
                'severity': 'BLOCKER' if s.get('severity') == 'CRITICAL' else 'MAJOR',
                'type': 'VULNERABILITY',
                'primaryLocation': {
                    'message': s.get('title', 'issue'),
                    'filePath': s.get('file', ''),
                    'textRange': { 'startLine': s.get('line', 1) }
                }
            })
        return { 'issues': issues }

from typing import Any, Dict, List

class SarifExporter:
    """SARIF 2.1.0 Standard Report Generator."""

    @classmethod
    def export_sarif(cls, security_issues: List[Dict[str, Any]], smells: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for issue in security_issues:
            rule_id = issue.get('cwe', 'CWE-UNKNOWN')
            results.append({
                'ruleId': rule_id,
                'level': 'error' if issue.get('severity') == 'CRITICAL' else 'warning',
                'message': { 'text': issue.get('title', 'issue') },
                'locations': [{
                    'physicalLocation': {
                        'artifactLocation': { 'uri': issue.get('file', '') },
                        'region': { 'startLine': issue.get('line', 1) }
                    }
                }]
            })
        return {
            '$schema': 'https://docs.oasis-open.org/sarif/sarif/v2.1.0/cos01/schemas/sarif-schema-2.1.0.json',
            'version': '2.1.0',
            'runs': [{
                'tool': { 'driver': { 'name': 'Codebase Navigator AI', 'version': '2.0.0' } },
                'results': results
            }]
        }

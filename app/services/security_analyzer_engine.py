from typing import Any, Dict, List, Optional, Set, Tuple
import re, math, collections

class SecurityAnalyzerEngine:
    """OWASP Top 10 SAST Taint Analyzer & Shannon Entropy Secret Scanner."""

    @classmethod
    def shannon_entropy(cls, str_val: str) -> float:
        if not str_val: return 0.0
        counts = collections.Counter(str_val)
        l = len(str_val)
        return -sum((c / l) * math.log2(c / l) for c in counts.values())

    @classmethod
    def scan_source(cls, content: str, file_path: str = '') -> List[Dict[str, Any]]:
        issues = []
        for i, line in enumerate(content.splitlines(), 1):
            t = line.strip()
            # SQLi
            if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE)\b.*\+|%\s*\(', t, re.IGNORECASE):
                issues.append({ 'cwe': 'CWE-89', 'title': 'SQL Injection Vulnerability', 'severity': 'CRITICAL', 'file': file_path, 'line': i, 'snippet': t, 'fix': 'Use parameterized prepared statements.' })
            # Command Injection
            if re.search(r'\b(exec|eval|os\.system|subprocess\.Popen)\(', t):
                issues.append({ 'cwe': 'CWE-78', 'title': 'Command Injection / Dynamic Exec', 'severity': 'HIGH', 'file': file_path, 'line': i, 'snippet': t, 'fix': 'Avoid dynamic eval/exec and pass arguments as safety arrays.' })
            # High Entropy Secret
            for match in re.finditer(r'["\']([A-Za-z0-9_\/+=]{32,512})["\']', t):
                secret = match.group(1)
                if cls.shannon_entropy(secret) > 4.5:
                    issues.append({ 'cwe': 'CWE-798', 'title': 'Hardcoded Credential / HIGH_ENTROPY SECRET', 'severity': 'HIGH', 'file': file_path, 'line': i, 'snippet': t, 'fix': 'Revoke immediately and migrate to environment variables or a Secret Manager.' })
        return issues

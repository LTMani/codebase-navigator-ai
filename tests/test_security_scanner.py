import pytest
from app.services.security_scanner import SecurityScanner


def test_security_scanner_rules():
    scanner = SecurityScanner()

    # Rule SEC-001 Hardcoded Secret
    assert scanner.rules[0]["pattern"].search("api_key = 'AIzaSyD28491823901823'")

    # Rule SEC-002 SQL Injection
    assert scanner.rules[1]["pattern"].search("cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')")

    # Rule SEC-003 Command Injection
    assert scanner.rules[2]["pattern"].search("subprocess.call(cmd, shell=True)")

    # Rule SEC-004 Insecure Deserialization
    assert scanner.rules[3]["pattern"].search("data = pickle.loads(raw_bytes)")

    # Rule SEC-005 Disabled SSL
    assert scanner.rules[4]["pattern"].search("requests.get(url, verify=False)")

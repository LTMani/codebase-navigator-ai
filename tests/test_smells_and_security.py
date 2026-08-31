import unittest
from app.services.smell_detector_service import SmellDetectorService
from app.services.security_analyzer_engine import SecurityAnalyzerEngine

class TestSmellsAndSecurity(unittest.TestCase):
    def test_smell_detection(self):
        files = [{
            'file_path': 'long_code.py',
            'functions': [{'name': 'mega_func', 'start_line': 1, 'end_line': 60, 'parameters': ['a', 'b', 'c', 'd', 'e', 'f']}],
            'classes': [{'name': 'GodManager', 'start_line': 1, 'end_line': 500}]
        }]
        smells = SmellDetectorService.detect_all_smells(files)
        smell_types = {s['smell'] for s in smells}
        self.assertIn('Long Method', smell_types)
        self.assertIn('Long Parameter List', smell_types)
        self.assertIn('God Class', smell_types)

    def test_security_scanner(self):
        code = 'cursor.execute("SELECT * FROM users WHERE id = " + user_input)\neval(untrusted_str)'
        issues = SecurityAnalyzerEngine.scan_source(code, 'app.py')
        cwes = {i['cwe'] for i in issues}
        self.assertIn('CWE-89', cwes)
        self.assertIn('CWE-78', cwes)

if __name__ == '__main__':
    unittest.main()

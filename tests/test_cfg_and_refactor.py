import unittest
from app.services.cfg_engine import CFGEngine
from app.services.refactoring_engine import RefactoringEngine

class TestCFGAndRefactor(unittest.TestCase):
    def test_cfg_builder(self):
        code = 'x = 1\nif x > 0:\n    print(x)\n'
        res = CFGEngine.build_python_cfg(code)
        self.assertTrue(res['success'])
        self.assertGreaterEqual(len(res['blocks']), 3)
        self.assertGreaterEqual(len(res['edges']), 2)

    def test_refactoring_diff(self):
        orig = 'def old_func():\n    return 42\n'
        new_c = 'def new_func():\n    return 42\n'
        diff = RefactoringEngine.generate_unified_diff(orig, new_c, 'test.py')
        self.assertIn('-def old_func():', diff)
        self.assertIn('+def new_func():', diff)

if __name__ == '__main__':
    unittest.main()

import unittest
from app.services.metrics_engine import MetricsEngine

class TestMetricsEngine(unittest.TestCase):
    def test_lcom4(self):
        methods = ['m1', 'm2', 'm3']
        fields = {
            'm1': {'f1'},
            'm2': {'f1', 'f2'},
            'm3': {'f3'}
        }
        comp = MetricsEngine.compute_lcom4(methods, fields)
        self.assertEqual(comp, 2)

    def test_martin_package_metrics(self):
        pkg_classes = {'A', 'B'}
        deps = [('A', 'External'), ('Client', 'B')]
        metrics = MetricsEngine.compute_martin_package_metrics(pkg_classes, deps, {'A'})
        self.assertEqual(metrics['ca'], 1)
        self.assertEqual(metrics['ce'], 1)
        self.assertEqual(metrics['instability'], 0.5)
        self.assertEqual(metrics['abstractness'], 0.5)

if __name__ == '__main__':
    unittest.main()

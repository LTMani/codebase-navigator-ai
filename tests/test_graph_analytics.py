import unittest
from app.services.graph_analytics_engine import GraphAnalyticsEngine

class TestGraphAnalytics(unittest.TestCase):
    def test_betweenness_centrality(self):
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D')]
        res = GraphAnalyticsEngine.compute_betweenness_centrality(nodes, edges)
        self.assertIn('B', res)
        self.assertIn('C', res)
        self.assertIsInstance(res['B'], float)

    def test_louvain_communities(self):
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('C', 'D')]
        comms = GraphAnalyticsEngine.detect_communities_louvain(nodes, edges)
        self.assertEqual(comms['A'], comms['B'])

    def test_dijkstra(self):
        edges = [('A', 'B'), ('B', 'C')]
        cost, path = GraphAnalyticsEngine.find_shortest_path_dijkstra('A', 'C', edges)
        self.assertEqual(cost, 2.0)
        self.assertEqual(path, ['A', 'B', 'C'])

    def test_articulation_points(self):
        nodes = ['A', 'B', 'C']
        edges = [('A', 'B'), ('B', 'C')]
        arts = GraphAnalyticsEngine.find_articulation_points(nodes, edges)
        self.assertIn('B', arts)

if __name__ == '__main__':
    unittest.main()

from typing import Any, Dict, List, Optional, Set, Tuple
import heapq, collections

class GraphAnalyticsEngine:
    """Advanced Graph algorithms: Brandes Betweenness, Louvain Modularity, Dijkstra, Tarjan Articulations."""

    @classmethod
    def compute_betweenness_centrality(cls, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, float]:
        adj = collections.defaultdict(set)
        for u, v in edges:
            adj[u].add(v)
        cb = { n: 0.0 for n in nodes }
        for s in nodes:
            S = []; P = { w: [] for w in nodes }; sigma = { w: 0 for w in nodes }; sigma[s] = 1
            d = { w: -1 for w in nodes }; d[s] = 0
            Q = collections.deque([s])
            while Q:
                v = Q.popleft(); S.append(v)
                for w in adj[v]:
                    if d[w] < 0:
                        Q.append(w); d[w] = d[v] + 1
                    if d[w] == d[v] + 1:
                        sigma[w] += sigma[v]; P[w].append(v)
            delta = { w: 0.0 for w in nodes }
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    cb[w] += delta[w]
        n = len(nodes)
        scale = 1.0 / ((n - 1) * (n - 2)) if n > 2 else 1.0
        return { k: round(v * scale, 4) for k, v in cb.items() }

    @classmethod
    def detect_communities_louvain(cls, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, int]:
        communities = { n: i for i, n in enumerate(nodes) }
        adj = collections.defaultdict(set)
        for u, v in edges:
            adj[u].add(v); adj[v].add(u)
        for _ in range(3):
            for n in nodes:
                neighbors = adj[n]
                if neighbors:
                    neighbor_comms = [communities[nb] for nb in neighbors]
                    most_common = collections.Counter(neighbor_comms).most_common(1)[0][0]
                    communities[n] = most_common
        return communities

    @classmethod
    def find_shortest_path_dijkstra(cls, start: str, target: str, edges: List[Tuple[str, str]]) -> Tuple[float, List[str]]:
        adj = collections.defaultdict(list)
        for u, v in edges:
            adj[u].append((v, 1.0))
        q = [(0.0, start, [start])]
        visited = set()
        while q:
            cost, curr, path = heapq.heappop(q)
            if curr in visited: continue
            visited.add(curr)
            if curr == target: return cost, path
            for next_n, w in adj[curr]:
                if next_n not in visited:
                    heapq.heappush(q, (cost + w, next_n, path + [next_n]))
        return float('inf'), []

    @classmethod
    def find_articulation_points(cls, nodes: List[str], edges: List[Tuple[str, str]]) -> Set[str]:
        adj = collections.defaultdict(set)
        for u, v in edges:
            adj[u].add(v); adj[v].add(u)
        time = 0
        disc = {}; low = {}; parent = {}
        articulation = set()
        def dfs(u):
            nonlocal time
            children = 0
            time += 1; disc[u] = low[u] = time
            for v in adj[u]:
                if v not in disc:
                    children += 1; parent[v] = u
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    if parent.get(u) is None and children > 1:
                        articulation.add(u)
                    if parent.get(u) is not None and low[v] >= disc[u]:
                        articulation.add(u)
                elif v != parent.get(u):
                    low[u] = min(low[u], disc[v])
        for n in nodes:
            if n not in disc: dfs(n)
        return articulation

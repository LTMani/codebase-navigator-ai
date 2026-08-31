from typing import Any, Dict, List, Optional, Set, Tuple
import math, collections

class MetricsEngine:
    """Production Software Metrics Engine: LCOM4, Martin CA, CE, I, A, D, Halstead, ABC."""

    @classmethod
    def compute_lcom4(cls, methods: List[str], fields_per_method: Dict[str, Set[str]]) -> int:
        if not methods: return 0
        if len(methods) == 1: return 1
        adj = collections.defaultdict(set)
        for i in range(len(methods)):
            for j in range(i + 1, len(methods)):
                m1, m2 = methods[i], methods[j]
                if fields_per_method.get(m1, set()) & fields_per_method.get(m2, set()):
                    adj[m1].add(m2); adj[m2].add(m1)
        visited = set()
        components = 0
        for m in methods:
            if m not in visited:
                components += 1
                q = collections.deque([m])
                while q:
                    curr = q.popleft()
                    if curr in visited: continue
                    visited.add(curr)
                    for next_m in adj[curr]:
                        if next_m not in visited: q.append(next_m)
        return components

    @classmethod
    def compute_martin_package_metrics(cls, classes_in_package: Set[str], all_dependencies: List[Tuple[str, str]], abstract_classes: Set[str]) -> Dict[str, float]:
        ca = 0; ce = 0
        for src, dst in all_dependencies:
            if src not in classes_in_package and dst in classes_in_package: ca += 1
            if src in classes_in_package and dst not in classes_in_package: ce += 1
        i = ce / (ca + ce) if (ca + ce) > 0 else 0.0
        a = len(abstract_classes & classes_in_package) / len(classes_in_package) if classes_in_package else 0.0
        d = abs(a + i - 1.0)
        return {"ca": ca, "ce": ce, "instability": round(i, 3), "abstractness": round(a, 3), "distance": round(d, 3), "normalized_distance": round(d / math.sqrt(2), 3) }

    @classmethod
    def compute_halstead_suite(cls, operators_count: Dict[str, int], operands_count: Dict[str, int]) -> Dict[str, float]:
        n1 = len(operators_count); n2 = len(operands_count)
        N1 = sum(operators_count.values()); N2 = sum(operands_count.values())
        vocab = n1 + n2; length = N1 + N2
        volume = length * math.log2(vocab) if vocab > 0 else 0.0
        difficulty = (n1 / 2.0) * (N2 / max(1, n2)) if n2 > 0 else 0.0
        effort = volume * difficulty
        bugs = volume / 3000.0
        return { "vocabulary": vocab, "length": length, "volume": round(volume, 2), "difficulty": round(difficulty, 2), "effort": round(effort, 2), "delivered_bugs": round(bugs, 3) }

import pytest
from app.services.dependency_service import DependencyService


def test_tarjan_scc_cycle_detection():
    service = DependencyService()

    # Graph with cycle: A -> B -> C -> A, and disconnected node D
    adj = {
        "A": {"B"},
        "B": {"C"},
        "C": {"A", "D"},
        "D": set(),
    }

    cycles, sccs = service._find_strongly_connected_components(adj)
    assert len(cycles) == 1
    cycle_nodes = set(cycles[0])
    assert cycle_nodes == {"A", "B", "C"}


def test_tarjan_scc_acyclic_graph():
    service = DependencyService()

    # DAG: A -> B -> C -> D
    adj = {
        "A": {"B"},
        "B": {"C"},
        "C": {"D"},
        "D": set(),
    }

    cycles, sccs = service._find_strongly_connected_components(adj)
    assert len(cycles) == 0

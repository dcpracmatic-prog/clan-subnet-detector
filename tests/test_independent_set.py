"""Basic verification of the independent-set planner and audit path."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clan_subnet_detector import Graph, gwmin_independent, is_independent, run_audit


def test_empty():
    g = Graph(n=0)
    assert gwmin_independent(g) == []


def test_no_edges():
    g = Graph(n=5)
    s = gwmin_independent(g)
    assert len(s) == 5
    assert is_independent(g, s)


def test_complete():
    g = Graph.from_edges(3, [(0, 1), (0, 2), (1, 2)])
    s = gwmin_independent(g)
    assert len(s) == 1
    assert is_independent(g, s)


def test_banned():
    g = Graph.from_edges(4, [(0, 1), (2, 3)])
    s = gwmin_independent(g, banned=[0, 2])
    assert 0 not in s and 2 not in s
    assert is_independent(g, s)


def test_audit_demo():
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 3),
        (0, 4),
        (3, 5),
        (7, 8), (8, 9),
    ]
    g = Graph.from_edges(n=10, edges=edges, directed=False)
    report = run_audit(g, independent_k=5)
    assert report.checks["all_findings_verified"] is True
    assert report.graph_n == 10
    assert any(f.kind == "clique" and f.verified for f in report.findings)
    assert any(f.kind == "independent_set" and f.verified for f in report.findings)


if __name__ == "__main__":
    test_empty()
    test_no_edges()
    test_complete()
    test_banned()
    test_audit_demo()
    print("All tests passed.")

"""Basic verification of the independent-set planner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph.graph import Graph
from detection.independent_set import gwmin_independent, is_independent


def test_empty():
    g = Graph(n=0)
    assert gwmin_independent(g) == []


def test_no_edges():
    g = Graph(n=5)
    s = gwmin_independent(g)
    assert len(s) == 5
    assert is_independent(g, s)


def test_complete():
    # K3
    g = Graph.from_edges(3, [(0, 1), (0, 2), (1, 2)])
    s = gwmin_independent(g)
    assert len(s) == 1
    assert is_independent(g, s)


def test_banned():
    g = Graph.from_edges(4, [(0, 1), (2, 3)])
    s = gwmin_independent(g, banned=[0, 2])
    assert 0 not in s and 2 not in s
    assert is_independent(g, s)


if __name__ == "__main__":
    test_empty()
    test_no_edges()
    test_complete()
    test_banned()
    print("All independent-set tests passed.")

"""Minimal edge-list loader."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from graph.graph import Graph


def load_edge_list(
    path: str | Path,
    directed: bool = False,
    weighted: bool = False,
) -> Graph:
    """Load a simple edge list.

    Format (whitespace-separated):
        u v          # unweighted
        u v w        # weighted (if weighted=True)

    Node identifiers may be arbitrary non-negative integers; they are
    remapped to a contiguous 0..n-1 range.
    """
    path = Path(path)
    raw_edges: List[Tuple[int, int, float]] = []
    nodes = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            u, v = int(parts[0]), int(parts[1])
            w = float(parts[2]) if weighted and len(parts) > 2 else 1.0
            raw_edges.append((u, v, w))
            nodes.add(u)
            nodes.add(v)

    if not nodes:
        return Graph(n=0, directed=directed)

    sorted_nodes = sorted(nodes)
    mapping = {old: new for new, old in enumerate(sorted_nodes)}
    n = len(sorted_nodes)
    g = Graph(n=n, directed=directed)
    for u, v, w in raw_edges:
        g.add_edge(mapping[u], mapping[v], w)
    return g

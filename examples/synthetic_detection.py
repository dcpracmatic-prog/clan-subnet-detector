#!/usr/bin/env python3
"""Minimal end-to-end example on a synthetic graph.

Creates a small graph containing:
- a dense clique (clan)
- a set of mutually non-adjacent nodes (isolated logical group)

Then runs the primitive detectors and prints scores.
"""

from __future__ import annotations

import sys
from pathlib import Path

# allow running from repository root without installation
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph.graph import Graph
from graph.metrics import connected_components, density
from detection.clique import greedy_clique, is_clique
from detection.independent_set import plan_independent, is_independent
from scoring.risk import score_clique, score_independent_set


def build_synthetic() -> Graph:
    # 0-1-2-3 form a clique of size 4
    # 4,5,6 form an independent set (no edges among them)
    # a few bridging edges
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 3),
        (0, 4),          # bridge
        (3, 5),          # bridge
        (7, 8), (8, 9),  # small path (another component-ish)
    ]
    return Graph.from_edges(n=10, edges=edges, directed=False)


def main() -> None:
    g = build_synthetic()
    print(f"Graph: n={g.n}, m={g.edge_count()}, density={density(g):.3f}")
    print(f"Connected components: {len(connected_components(g))}")

    # Clique detection
    clique = greedy_clique(g)
    print(f"\nGreedy clique: {clique}  (size={len(clique)})")
    print(f"  is_clique = {is_clique(g, clique)}")
    print(f"  risk score = {score_clique(g, clique):.2f}")

    # Independent-set detection (isolated logical group)
    ind = plan_independent(g, k=5)
    print(f"\nIndependent set (GWMIN, k≤5): {ind}")
    print(f"  is_independent = {is_independent(g, ind)}")
    print(f"  isolation score = {score_independent_set(g, ind):.2f}")


if __name__ == "__main__":
    main()

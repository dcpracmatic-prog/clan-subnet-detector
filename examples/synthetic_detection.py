#!/usr/bin/env python3
"""Minimal end-to-end example (also usable as a smoke test).

Prefer the CLI for audit reports:
  python -m clan_subnet_detector.cli --demo --out results/
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running without installation
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clan_subnet_detector import (
    Graph,
    greedy_clique,
    plan_independent,
    is_clique,
    is_independent,
    score_clique,
    score_independent_set,
    density,
    connected_components,
    run_audit,
)


def build_synthetic() -> Graph:
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 3),
        (0, 4),
        (3, 5),
        (7, 8), (8, 9),
    ]
    return Graph.from_edges(n=10, edges=edges, directed=False)


def main() -> None:
    g = build_synthetic()
    print(f"Graph: n={g.n}, m={g.edge_count()}, density={density(g):.3f}")
    print(f"Connected components: {len(connected_components(g))}")

    clique = greedy_clique(g)
    print(f"\nGreedy clique: {clique}  (size={len(clique)})")
    print(f"  is_clique = {is_clique(g, clique)}")
    print(f"  risk score = {score_clique(g, clique):.2f}")

    ind = plan_independent(g, k=5)
    print(f"\nIndependent set (GWMIN, k≤5): {ind}")
    print(f"  is_independent = {is_independent(g, ind)}")
    print(f"  isolation score = {score_independent_set(g, ind):.2f}")

    print("\n--- Audit report (simplified) ---")
    report = run_audit(g, independent_k=5)
    print(report.to_markdown())


if __name__ == "__main__":
    main()

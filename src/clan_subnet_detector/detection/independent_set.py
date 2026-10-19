"""Independent-set planners.

Primary use-case: groups of nodes that do not communicate (isolated logical
subnetworks). Supports GWMIN (pure Python) and MORPH (compiled binary).
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Set

from ..graph.graph import Graph


def gwmin_independent(
    g: Graph,
    banned: Optional[Iterable[int]] = None,
    k: Optional[int] = None,
    weights: Optional[Sequence[float]] = None,
) -> List[int]:
    """GWMIN greedy independent set (weight / (degree + 1))."""
    n = g.n
    banned_set: Set[int] = set(banned or [])
    alive = [i not in banned_set for i in range(n)]
    w = list(weights) if weights is not None else [1.0] * n
    if len(w) != n:
        raise ValueError("weights length must equal number of nodes")

    deg = [0] * n
    for u in range(n):
        if not alive[u]:
            continue
        for v in g.adj[u]:
            if alive[v]:
                deg[u] += 1

    picked: List[int] = []
    while True:
        if k is not None and len(picked) >= k:
            break
        best = -1
        best_score = -1.0
        for v in range(n):
            if not alive[v]:
                continue
            score = w[v] / (deg[v] + 1)
            if score > best_score:
                best_score = score
                best = v
        if best < 0:
            break
        picked.append(best)
        alive[best] = False
        for u in list(g.adj[best].keys()):
            if alive[u]:
                alive[u] = False
                for x in g.adj[u]:
                    if alive[x]:
                        deg[x] -= 1
        if g.directed:
            for u in range(n):
                if alive[u] and best in g.adj[u]:
                    alive[u] = False
                    for x in g.adj[u]:
                        if alive[x]:
                            deg[x] -= 1
    return picked


def plan_independent(
    g: Graph,
    banned: Optional[Iterable[int]] = None,
    k: Optional[int] = None,
    weights: Optional[Sequence[float]] = None,
    method: str = "gwmin",
    budget_ms: int = 100,
    seed: int = 1,
) -> List[int]:
    """Public planner interface.

    Methods
    -------
    gwmin : pure-Python GWMIN heuristic (always available).
    morph : call compiled MORPH binary (dump_morph). Falls back to gwmin
            if the binary is missing or fails.
    """
    if method == "gwmin":
        return gwmin_independent(g, banned=banned, k=k, weights=weights)
    if method == "morph":
        try:
            from .morph_adapter import morph_independent
            return morph_independent(
                g, banned=banned, k=k, budget_ms=budget_ms, seed=seed
            )
        except Exception:
            # graceful degradation — keep the audit path alive
            return gwmin_independent(g, banned=banned, k=k, weights=weights)
    raise ValueError(f"unknown independent-set method: {method}")


def is_independent(g: Graph, nodes: Iterable[int]) -> bool:
    """Verify that the given set of nodes forms an independent set."""
    node_set = set(nodes)
    for u in node_set:
        for v in g.adj[u]:
            if v in node_set and u != v:
                return False
    return True

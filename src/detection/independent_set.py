"""Independent-set planners.

The primary use-case is the discovery of groups of nodes that do not
communicate with one another (isolated logical subnetworks).

A lightweight GWMIN-style greedy heuristic is provided as a stand-in.
It can later be replaced or complemented by a call to a compiled
MORPH binary (morph_qoblib_solver) that accepts .gph format.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Set

from graph.graph import Graph


def gwmin_independent(
    g: Graph,
    banned: Optional[Iterable[int]] = None,
    k: Optional[int] = None,
    weights: Optional[Sequence[float]] = None,
) -> List[int]:
    """GWMIN greedy independent set (weight / (degree + 1)).

    Parameters
    ----------
    g : Graph
        Input graph (treated as undirected for independence).
    banned : iterable of int, optional
        Nodes that must not be selected.
    k : int, optional
        Maximum number of nodes to return.  None = unlimited.
    weights : sequence of float, optional
        Node weights (higher = preferred).  Default = 1.0 for all.

    Returns
    -------
    list of int
        Selected node indices forming an independent set.
    """
    n = g.n
    banned_set: Set[int] = set(banned or [])
    alive = [i not in banned_set for i in range(n)]
    w = list(weights) if weights is not None else [1.0] * n
    if len(w) != n:
        raise ValueError("weights length must equal number of nodes")

    # current degree among alive nodes
    deg = [0] * n
    for u in range(n):
        if not alive[u]:
            continue
        for v in g.adj[u]:
            if alive[v] and (not g.directed or True):  # undirected view
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
        # remove neighbours
        for u in list(g.adj[best].keys()):
            if alive[u]:
                alive[u] = False
                for x in g.adj[u]:
                    if alive[x]:
                        deg[x] -= 1
        # also reverse edges if directed
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
) -> List[int]:
    """Public planner interface.

    Currently only 'gwmin' is implemented.  Future values may include
    'morph' (external binary) or other heuristics.
    """
    if method == "gwmin":
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

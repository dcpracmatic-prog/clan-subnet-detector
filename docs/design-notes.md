# Design notes (primitive stage)

## Graph model

- Nodes identified by contiguous integers `0 … n-1`.
- Edges may be weighted; directed flag is supported but most independence and clique checks currently use an undirected view.
- Node attributes are stored in a simple dictionary for future extension (reputation, geolocation, identity labels).

## Detection strategy

1. **Cliques** – greedy construction from high-degree seeds; later Bron-Kerbosch or densest-subgraph approximations.
2. **Independent sets** – GWMIN stand-in (`weight / (degree+1)`). Designed so that a compiled MORPH binary can be substituted via the same `plan_independent` interface.
3. **Components & communities** – basic BFS components already present; Louvain/Leiden planned.

## Verification discipline

Every reported structure must be independently checkable:

- `is_clique(g, nodes)`
- `is_independent(g, nodes)`

This mirrors the verification approach used for MORPH on QOBLIB instances.

## Future integration points

- Policy-bound containment actions (signed bindings in the style of ChannelGuardian / TDCP).
- Streaming ingestion adapters.
- Temporal windowing and change-point detection on community / clique evolution.

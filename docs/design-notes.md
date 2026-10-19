# Design notes – MVP stage

## Audit model

The core guarantee of this MVP is:

> Every structure that appears in an `AuditReport` has been re-checked by a pure function (`is_clique` or `is_independent`) that only reads the original graph and the candidate node list.

Detectors may be replaced or improved later; the verification layer stays.

## Graph model

- Nodes: contiguous integers `0 … n-1`.
- Edges: optional weight; directed flag supported (most independence/clique checks currently use an undirected view).
- Node attributes: simple dict for future reputation / geo / identity labels.

## Detectors (current)

1. **Clique** – greedy construction from a high-degree (or supplied) seed.
2. **Independent set** – GWMIN (`weight / (degree+1)`). Interface accepts a `method` string so a compiled MORPH binary can be plugged in later without changing the audit path.

## Scoring

Scores are intentionally simple and transparent so that a later policy / containment layer can reason about them without reverse-engineering opaque models.

## Next natural increments

- Temporal windowing and change detection on findings.
- Community detection (Louvain / Leiden) with cut-based isolation metrics.
- Streaming / NetFlow adapters.
- Optional call-out to a MORPH binary for higher-quality independent sets.
- Signed policy bindings for containment actions (ChannelGuardian / TDCP style).

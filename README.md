# Clan-Subnet Detector

**Primitive repository** for a cybersecurity and network-analysis system focused on the detection of **cliques (clanes)** and **isolated subnetworks** in internet traffic graphs and social-network interaction graphs.

This project builds on independent-set heuristics (MORPH-style planners), conflict-graph modelling, and graph-theoretic primitives already validated in related work (QOBLIB-style verification, ChannelGuardian failover concepts).

## Objectives

- Model communication or interaction data as (directed/undirected, weighted) graphs.
- Detect dense groups (**cliques** / high-density subgraphs) that may indicate coordinated activity, C2 clusters, or closed communities.
- Detect **isolated subnetworks**: connected components, low-cut communities, and large independent / quasi-independent sets (nodes that do not communicate with one another).
- Score findings by size, density, isolation (cut size), temporal evolution and external reputation signals.
- Provide a verifiable, reproducible core that can later integrate policy bindings and signed containment actions.

## Current status (primitive / scaffolding)

This repository contains only the initial skeleton:

- Project layout and module boundaries
- Core data structures for graphs
- Placeholder interfaces for detection algorithms
- Basic independent-set planner stub (GWMIN-style, ready for MORPH integration)
- Minimal CLI and example entry points
- Test and documentation placeholders

No production-grade performance, persistence or SIEM integration is present yet.

## Repository layout

```
clan-subnet-detector/
├── src/
│   ├── graph/          # Graph representation, loaders, basic metrics
│   ├── detection/      # Clique, community, independent-set algorithms
│   ├── scoring/        # Risk scoring and ranking of findings
│   ├── ingest/         # Traffic / social-graph ingestion adapters (stubs)
│   └── utils/          # Shared helpers
├── tests/              # Unit and property-style checks
├── examples/           # Runnable examples and synthetic scenarios
├── docs/               # Design notes and algorithm references
├── scripts/            # Build, benchmark and validation helpers
├── data/samples/       # Small synthetic graphs for local testing
├── README.md
├── pyproject.toml      # (or package.json / Cargo.toml later)
└── LICENSE
```

## Quick start (development)

```bash
# Python environment (recommended for the first prototype)
python -m venv .venv
source .venv/bin/activate   # or equivalent on Windows
pip install -e ".[dev]"

# Run a minimal example
python -m examples.synthetic_detection
```

## Design principles

1. **Correctness first** – every reported clique or independent set must be independently verifiable against the input graph (same discipline applied to MORPH / QOBLIB).
2. **Separation of concerns** – ingestion, graph model, detection algorithms, scoring and output are distinct layers.
3. **Pluggable planners** – the independent-set component accepts both the lightweight GWMIN stub and a future call to a compiled MORPH binary.
4. **Reproducibility** – seeds, budgets and exact graph snapshots are recorded with every result.
5. **Minimal external surface** – the core library has few mandatory dependencies; optional adapters (NetFlow, PCAP summaries, social APIs) are isolated.

## Roadmap (high level)

1. Solidify graph model + loaders for edge-list / adjacency formats.
2. Implement and verify clique heuristics and independent-set planner.
3. Add community detection (Louvain / Leiden) and cut-based isolation metrics.
4. Temporal windowing and change detection.
5. Scoring model and simple alerting interface.
6. Integration points for policy-signed containment (ChannelGuardian / TDCP style).
7. Performance scaling and streaming ingestion.

## Related projects

- MORPH – Maximum Independent Set heuristics and QOBLIB validation.
- ChannelGuardian / TDCP – policy-bound channel isolation and failover.
- Centinela – hardware-validation style probes (methodological inspiration for pre-job diagnostics).

## License

See `LICENSE` (to be chosen; currently placeholder).

## Author / Maintainer

dcpracmatic-prog

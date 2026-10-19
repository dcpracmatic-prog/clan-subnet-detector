# Clan-Subnet Detector (MVP)

**MVP auditable** for detection of **cliques (clanes)** and **isolated subnetworks** in communication / interaction graphs (internet traffic, social networks).

Every reported structure is **independently re-verified** against the original graph before it is accepted into the audit report. The goal is a small, reproducible core that a third party can audit without trusting the internal detector implementation.

## What the MVP does

1. Loads a graph (edge-list or built-in synthetic demo).
2. Runs two detectors:
   - Greedy clique construction.
   - Independent-set planner (GWMIN stand-in; interface ready for a MORPH binary later).
3. **Independently verifies** each result (`is_clique` / `is_independent`).
4. Computes transparent risk / isolation scores.
5. Emits a machine-readable **audit report** (JSON + Markdown) containing:
   - Environment snapshot (version, Python, platform)
   - Graph summary (n, m, density, components)
   - Every finding with its verification flag
   - Automated PASS/FAIL checks

## Quick start

```bash
# From repository root (no install required for the smoke path)
export PYTHONPATH=src
python -m clan_subnet_detector.cli --demo --out results/

# Or run the smoke script
./scripts/smoke_test.sh
```

Example with your own edge-list:

```bash
python -m clan_subnet_detector.cli --edge-list data/samples/small_clan.edgelist --out results/
```

## Audit contract (simplified)

| Check                         | Meaning                                              |
|-------------------------------|------------------------------------------------------|
| `clique_verified`             | Returned nodes form a true clique in the input graph |
| `independent_set_verified`    | Returned nodes form a true independent set           |
| `all_findings_verified`       | Both of the above succeeded                          |
| `graph_non_empty`             | Input contained at least one node                    |

If any verification fails the CLI exits with status 1 and the report records the failure explicitly.

Reports are written to:

- `results/AUDIT_REPORT.md` – human-readable
- `results/audit_report.json` – machine-readable

## Package layout

```
src/clan_subnet_detector/
├── graph/          # Graph model + basic metrics
├── detection/      # Clique + independent-set algorithms + verifiers
├── scoring/        # Transparent risk / isolation scores
├── ingest/         # Edge-list loader
├── audit/          # run_audit() + AuditReport (JSON/Markdown)
└── cli.py          # Minimal command-line entry point
```

## Design principles retained from related work

- **Correctness before performance** – verification is mandatory, not optional.
- **Reproducibility** – report captures version, platform and exact findings.
- **Pluggable planners** – independent-set path accepts a method flag; GWMIN is the current stand-in for a future MORPH call.
- **Minimal surface** – pure Python, no mandatory third-party runtime dependencies.

## Status

- Version: `0.1.0-mvp`
- Scope: single-shot detection + independent verification + audit report.
- Not yet included: temporal windows, streaming ingestion, SIEM adapters, signed policy bindings, production-scale optimisations.

## Related projects

- MORPH – Maximum Independent Set heuristics and QOBLIB-style validation.
- ChannelGuardian / TDCP – policy-bound channel isolation concepts.
- Centinela – methodological inspiration for diagnostic / pre-job probes.

## License

See `LICENSE` (proprietary placeholder until formal terms are defined).

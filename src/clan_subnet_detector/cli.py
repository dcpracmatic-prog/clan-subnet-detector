"""Minimal CLI for the MVP.

Usage examples:
  python -m clan_subnet_detector.cli --edge-list data/samples/small_clan.edgelist --out results/
  python -m clan_subnet_detector.cli --demo --out results/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit.report import run_audit, write_report
from .graph.graph import Graph
from .ingest.edge_list import load_edge_list


def build_demo_graph() -> Graph:
    """Small synthetic graph used by --demo and by smoke tests."""
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 3),
        (0, 4),
        (3, 5),
        (7, 8), (8, 9),
    ]
    return Graph.from_edges(n=10, edges=edges, directed=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clan-subnet-detector",
        description="MVP detector of cliques and isolated subnetworks with simplified audit report.",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--edge-list", type=Path, help="Path to whitespace edge-list file")
    src.add_argument("--demo", action="store_true", help="Run on the built-in synthetic graph")
    parser.add_argument("--out", type=Path, default=Path("results"), help="Directory for audit reports")
    parser.add_argument("--directed", action="store_true", help="Treat edge-list as directed")
    parser.add_argument("--independent-k", type=int, default=10, help="Max size for independent-set planner")
    parser.add_argument("--json-only", action="store_true", help="Print only the JSON report to stdout")
    args = parser.parse_args(argv)

    if args.demo:
        g = build_demo_graph()
    else:
        if not args.edge_list.exists():
            print(f"Error: file not found: {args.edge_list}", file=sys.stderr)
            return 2
        g = load_edge_list(args.edge_list, directed=args.directed)

    report = run_audit(g, independent_k=args.independent_k)
    paths = write_report(report, args.out)

    if args.json_only:
        print(report.to_json())
    else:
        print(report.to_markdown())
        print(f"\nReports written:\n  - {paths['markdown']}\n  - {paths['json']}")

    # Exit non-zero if any verification failed
    if not report.checks.get("all_findings_verified", False):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Minimal CLI for the MVP.

Examples:
  python -m clan_subnet_detector.cli --demo --out results/
  python -m clan_subnet_detector.cli --edge-list data/samples/small_clan.edgelist --method morph --out results/
  python -m clan_subnet_detector.cli --demo --sign-hmac secret123 --out results/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit.report import run_audit, write_report
from .audit.signing import sign_report_hmac
from .graph.graph import Graph
from .ingest.edge_list import load_edge_list, load_timestamped_edge_list


def build_demo_graph() -> Graph:
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
    src.add_argument("--timestamped", type=Path, help="Timestamped edge-list (u v ts [w])")
    src.add_argument("--demo", action="store_true", help="Run on the built-in synthetic graph")
    parser.add_argument("--out", type=Path, default=Path("results"), help="Directory for audit reports")
    parser.add_argument("--directed", action="store_true", help="Treat edge-list as directed")
    parser.add_argument("--independent-k", type=int, default=10, help="Max size for independent-set planner")
    parser.add_argument("--method", choices=["gwmin", "morph"], default="gwmin", help="Independent-set planner")
    parser.add_argument("--budget-ms", type=int, default=100, help="MORPH budget in milliseconds")
    parser.add_argument("--window", type=float, nargs=2, metavar=("T0", "T1"), help="Time window for --timestamped")
    parser.add_argument("--sign-hmac", type=str, default=None, help="HMAC secret to sign the audit report")
    parser.add_argument("--json-only", action="store_true", help="Print only the JSON report to stdout")
    args = parser.parse_args(argv)

    if args.demo:
        g = build_demo_graph()
    elif args.timestamped:
        tg = load_timestamped_edge_list(args.timestamped, directed=args.directed)
        if args.window:
            g = tg.window(args.window[0], args.window[1])
        else:
            t0, t1 = tg.time_range()
            g = tg.window(t0, t1)
    else:
        if not args.edge_list.exists():
            print(f"Error: file not found: {args.edge_list}", file=sys.stderr)
            return 2
        g = load_edge_list(args.edge_list, directed=args.directed)

    report = run_audit(
        g,
        independent_k=args.independent_k,
        method=args.method,
        budget_ms=args.budget_ms,
    )
    paths = write_report(report, args.out)

    if args.sign_hmac:
        signed = sign_report_hmac(report, args.sign_hmac.encode("utf-8"))
        signed_path = Path(args.out) / "audit_report.signed.json"
        signed_path.write_text(signed.to_json(), encoding="utf-8")
        paths["signed"] = signed_path

    if args.json_only:
        print(report.to_json())
    else:
        print(report.to_markdown())
        print(f"\nReports written:")
        for k, p in paths.items():
            print(f"  - {k}: {p}")

    if not report.checks.get("all_findings_verified", False):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for morph adapter fallback, dense detectors, temporal windows, signing."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clan_subnet_detector import (
    Graph,
    TemporalGraph,
    plan_independent,
    is_independent,
    k_core,
    densest_subgraph_peeling,
    run_audit,
    sign_report_hmac,
    verify_report_hmac,
    load_timestamped_edge_list,
)


def test_plan_morph_fallback():
    g = Graph.from_edges(5, [(0, 1), (2, 3)])
    # morph falls back to gwmin if binary path wrong / fails
    s = plan_independent(g, method="morph", budget_ms=10)
    assert is_independent(g, s)


def test_k_core_and_dense():
    # complete K4 + pendant
    edges = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3),(3,4)]
    g = Graph.from_edges(5, edges)
    core = k_core(g, 3)
    assert set(core) == {0, 1, 2, 3}
    nodes, dens = densest_subgraph_peeling(g)
    assert dens > 0
    assert len(nodes) >= 3


def test_temporal_window():
    tg = TemporalGraph(n=4)
    tg.add_event(0, 1, 10)
    tg.add_event(1, 2, 20)
    tg.add_event(2, 3, 30)
    g = tg.window(15, 25)
    assert g.edge_count() == 1
    assert g.has_edge(1, 2)


def test_signing_roundtrip():
    g = Graph.from_edges(4, [(0, 1), (0, 2), (1, 2)])
    report = run_audit(g, independent_k=3, include_dense=True)
    secret = b"test-secret-key"
    signed = sign_report_hmac(report, secret, kid="test")
    assert verify_report_hmac(signed, secret)
    assert not verify_report_hmac(signed, b"wrong")


def test_audit_with_dense():
    edges = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3),(0,4),(3,5),(7,8),(8,9)]
    g = Graph.from_edges(10, edges)
    report = run_audit(g, method="gwmin", independent_k=5, include_dense=True)
    kinds = {f.kind for f in report.findings}
    assert "clique" in kinds and "independent_set" in kinds
    assert "k_core" in kinds and "densest_subgraph" in kinds
    assert report.checks["all_findings_verified"]


if __name__ == "__main__":
    test_plan_morph_fallback()
    test_k_core_and_dense()
    test_temporal_window()
    test_signing_roundtrip()
    test_audit_with_dense()
    print("All v2 tests passed.")

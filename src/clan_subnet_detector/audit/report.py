"""Simplified audit pipeline for the MVP.

Produces a self-contained, machine-readable report that an independent
reviewer can re-verify without trusting the detector implementation.
"""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .. import __version__
from ..detection.clique import greedy_clique, is_clique
from ..detection.independent_set import is_independent, plan_independent
from ..graph.graph import Graph
from ..graph.metrics import connected_components, density
from ..scoring.risk import score_clique, score_independent_set


@dataclass
class Finding:
    kind: str                    # "clique" | "independent_set"
    nodes: List[int]
    size: int
    verified: bool               # independent check passed
    score: float
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Complete audit snapshot of a single run."""
    timestamp_utc: str
    version: str
    python: str
    platform: str
    graph_n: int
    graph_m: int
    graph_density: float
    n_components: int
    findings: List[Finding]
    checks: Dict[str, bool]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        lines = [
            "# Clan-Subnet Detector – Audit Report",
            "",
            f"- **Timestamp (UTC)**: {self.timestamp_utc}",
            f"- **Package version**: {self.version}",
            f"- **Python**: {self.python}",
            f"- **Platform**: {self.platform}",
            "",
            "## Graph summary",
            f"- Nodes (n): {self.graph_n}",
            f"- Edges (m): {self.graph_m}",
            f"- Density: {self.graph_density:.4f}",
            f"- Connected components: {self.n_components}",
            "",
            "## Automated checks",
        ]
        for k, v in self.checks.items():
            status = "PASS" if v else "FAIL"
            lines.append(f"- `{k}`: **{status}**")
        lines += ["", "## Findings"]
        if not self.findings:
            lines.append("_No findings recorded._")
        for i, f in enumerate(self.findings, 1):
            lines += [
                f"### {i}. {f.kind} (size={f.size})",
                f"- Nodes: `{f.nodes}`",
                f"- Independently verified: **{'yes' if f.verified else 'NO'}**",
                f"- Score: {f.score:.4f}",
            ]
            if f.extra:
                lines.append(f"- Extra: `{f.extra}`")
            lines.append("")
        if self.notes:
            lines += ["## Notes"] + [f"- {n}" for n in self.notes]
        return "\n".join(lines)


def run_audit(
    g: Graph,
    *,
    clique_seed: Optional[int] = None,
    independent_k: Optional[int] = 10,
    method: str = "gwmin",
) -> AuditReport:
    """Run detectors, verify every result independently, and build a report.

    The verification step (`is_clique` / `is_independent`) does not rely on
    the internal state of the detectors; it re-checks the returned node sets
    against the original graph. This is the core of the simplified audit.
    """
    notes: List[str] = []
    findings: List[Finding] = []

    # --- Clique ---
    clique_nodes = greedy_clique(g, seed=clique_seed)
    clique_ok = is_clique(g, clique_nodes)
    findings.append(
        Finding(
            kind="clique",
            nodes=list(clique_nodes),
            size=len(clique_nodes),
            verified=clique_ok,
            score=score_clique(g, clique_nodes),
            extra={"seed": clique_seed},
        )
    )
    if not clique_ok:
        notes.append("Clique candidate failed independent verification.")

    # --- Independent set ---
    ind_nodes = plan_independent(g, k=independent_k, method=method)
    ind_ok = is_independent(g, ind_nodes)
    findings.append(
        Finding(
            kind="independent_set",
            nodes=list(ind_nodes),
            size=len(ind_nodes),
            verified=ind_ok,
            score=score_independent_set(g, ind_nodes),
            extra={"method": method, "k": independent_k},
        )
    )
    if not ind_ok:
        notes.append("Independent-set candidate failed independent verification.")

    comps = connected_components(g)
    checks = {
        "all_findings_verified": all(f.verified for f in findings),
        "clique_verified": clique_ok,
        "independent_set_verified": ind_ok,
        "graph_non_empty": g.n > 0,
    }

    return AuditReport(
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        version=__version__,
        python=sys.version.split()[0],
        platform=platform.platform(),
        graph_n=g.n,
        graph_m=g.edge_count(),
        graph_density=density(g),
        n_components=len(comps),
        findings=findings,
        checks=checks,
        notes=notes,
    )


def write_report(report: AuditReport, out_dir: str | Path) -> Dict[str, Path]:
    """Write JSON + Markdown report files. Returns paths written."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "audit_report.json"
    md_path = out / "AUDIT_REPORT.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

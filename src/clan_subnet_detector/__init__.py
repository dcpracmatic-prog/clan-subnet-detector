"""Clan-Subnet Detector – MVP package for clique and isolated-subnet detection.

Designed for simplified independent audit: every reported structure is
re-checked against the original graph before being accepted into the report.
"""

__version__ = "0.1.0-mvp"

from .graph.graph import Graph, Edge
from .graph.metrics import density, degree_sequence, connected_components
from .detection.independent_set import plan_independent, gwmin_independent, is_independent
from .detection.clique import greedy_clique, is_clique
from .scoring.risk import score_clique, score_independent_set
from .audit.report import run_audit, AuditReport
from .ingest.edge_list import load_edge_list

__all__ = [
    "Graph",
    "Edge",
    "density",
    "degree_sequence",
    "connected_components",
    "plan_independent",
    "gwmin_independent",
    "is_independent",
    "greedy_clique",
    "is_clique",
    "score_clique",
    "score_independent_set",
    "run_audit",
    "AuditReport",
    "load_edge_list",
    "__version__",
]

"""Ingestion adapters (stubs).

Future implementations will cover:
- NetFlow / IPFIX summaries
- PCAP-derived flow graphs
- Social-interaction edge lists
- Streaming event sources
"""

from .edge_list import load_edge_list

__all__ = ["load_edge_list"]

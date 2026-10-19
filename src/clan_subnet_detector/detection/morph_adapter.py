"""Adapter to the compiled MORPH binary (morph_qoblib_solver / dump_morph).

Writes a temporary .gph file, invokes the solver, and returns the selected
vertices. Falls back gracefully when the binary is unavailable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from ..graph.graph import Graph


def graph_to_gph(g: Graph, path: Path) -> None:
    """Write graph in DIMACS-like .gph format expected by MORPH (1-indexed edges)."""
    # undirected view: emit each undirected edge once
    lines = [f"p edge {g.n} {g.edge_count()}"]
    seen = set()
    for u in range(g.n):
        for v in g.adj[u]:
            if u == v:
                continue
            a, b = (u, v) if u < v else (v, u)
            if (a, b) in seen:
                continue
            seen.add((a, b))
            lines.append(f"e {a + 1} {b + 1}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_morph_binary() -> Optional[Path]:
    """Locate dump_morph or morph_qoblib_solver on PATH / env / common locations."""
    env = os.environ.get("MORPH_DUMP_BIN") or os.environ.get("MORPH_BIN")
    if env:
        p = Path(env)
        if p.is_file() and os.access(p, os.X_OK):
            return p
    for name in ("dump_morph", "morph_qoblib_solver"):
        found = shutil.which(name)
        if found:
            return Path(found)
    # common relative locations from clan-subnet-detector or artifacts
    candidates = [
        Path("/home/workdir/artifacts/MORPH/dump_morph"),
        Path("/home/workdir/artifacts/MORPH/morph_qoblib_solver"),
        Path.cwd() / "dump_morph",
        Path.cwd().parent / "MORPH" / "dump_morph",
    ]
    for p in candidates:
        if p.is_file() and os.access(p, os.X_OK):
            return p
    return None


def morph_independent(
    g: Graph,
    banned: Optional[Iterable[int]] = None,
    k: Optional[int] = None,
    budget_ms: int = 100,
    seed: int = 1,
    binary: Optional[Path] = None,
) -> List[int]:
    """Call MORPH and return an independent set (0-indexed vertices).

    If `banned` is non-empty, those nodes are removed from the graph before
    solving (by inducing the complement). If `k` is set, the result is truncated.
    """
    bin_path = binary or find_morph_binary()
    if bin_path is None:
        raise FileNotFoundError(
            "MORPH binary not found. Set MORPH_DUMP_BIN or place dump_morph on PATH."
        )

    banned_set = set(banned or [])
    if banned_set:
        keep = [i for i in range(g.n) if i not in banned_set]
        mapping = {old: new for new, old in enumerate(keep)}
        inv = {new: old for old, new in mapping.items()}
        sub = g.induced_subgraph(keep)
        work = sub
    else:
        mapping = inv = None
        work = g

    if work.n == 0:
        return []

    with tempfile.TemporaryDirectory(prefix="morph_") as td:
        gph = Path(td) / "g.gph"
        graph_to_gph(work, gph)
        # Prefer dump_morph (prints vertices). morph_qoblib_solver only prints size.
        is_dump = "dump" in bin_path.name
        if is_dump:
            cmd = [str(bin_path), str(gph), str(budget_ms), str(seed)]
        else:
            # size-only binary cannot supply vertices; signal caller to fall back
            raise RuntimeError(
                f"{bin_path.name} does not emit vertices; use dump_morph instead"
            )
        try:
            out = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=max(5.0, budget_ms / 1000.0 + 30.0),
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"MORPH timed out after budget={budget_ms}ms") from e
        if out.returncode != 0:
            raise RuntimeError(
                f"MORPH failed (rc={out.returncode}): {out.stderr[:400]}"
            )
        verts: List[int] = []
        for line in out.stdout.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("c"):
                continue
            try:
                # dump prints 1-indexed
                verts.append(int(s) - 1)
            except ValueError:
                continue

    if inv is not None:
        verts = [inv[v] for v in verts if v in inv]
    if k is not None and len(verts) > k:
        verts = verts[:k]
    return verts

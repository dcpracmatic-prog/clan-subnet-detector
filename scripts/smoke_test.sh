#!/usr/bin/env bash
# Simplified smoke + audit check for the MVP.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

echo "== 1. Unit tests =="
python tests/test_independent_set.py

echo ""
echo "== 2. Demo audit (CLI) =="
python -m clan_subnet_detector.cli --demo --out /tmp/clan_mvp_results
echo ""
echo "Smoke test finished. Reports in /tmp/clan_mvp_results/"

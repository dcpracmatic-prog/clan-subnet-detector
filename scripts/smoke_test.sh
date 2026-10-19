#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

echo "== 1. Unit tests =="
python tests/test_independent_set.py
python tests/test_mvp_v2.py

echo ""
echo "== 2. Demo audit (CLI, gwmin) =="
python -m clan_subnet_detector.cli --demo --out /tmp/clan_mvp_results --sign-hmac smoke-secret

echo ""
echo "== 3. Temporal window =="
python -m clan_subnet_detector.cli --timestamped data/samples/small_temporal.edgelist \
  --window 100 150 --out /tmp/clan_mvp_temporal

echo ""
echo "Smoke test finished."

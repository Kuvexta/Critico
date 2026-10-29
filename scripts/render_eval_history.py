"""CLI del dashboard histórico: snapshot + render (make eval-history)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # LA-06
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Snapshot + render del dashboard histórico de evals")
    ap.add_argument("--history", default=str(BASE / "history"), help="directorio de snapshots")
    ap.add_argument("--out", default=str(BASE / "dashboard-evals.html"), help="salida HTML")
    ap.add_argument("--metrics", help="JSON con métricas para snapshot (opcional)")
    args = ap.parse_args()

    from evals import history as hist, html_history
    if args.metrics:
        import json
        hist.snapshot(json.loads(Path(args.metrics).read_text(encoding="utf-8")), args.history)
    data = hist.load_history(args.history)
    Path(args.out).write_text(html_history.render_dashboard(data), encoding="utf-8")
    print(f"dashboard: {args.out} ({len(data)} snapshots)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""CLI del dashboard histórico: snapshot + render + prune (make eval-history)."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # LA-06
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Dashboard histórico de evals (snapshot + render)")
    ap.add_argument("--history", default=str(BASE / "history"), help="directorio de snapshots")
    ap.add_argument("--out", default=str(BASE / "dashboard-evals.html"), help="salida HTML")
    ap.add_argument("--cases", default=str(BASE / "09_golden_set" / "cases"))
    ap.add_argument("--snapshot", action="store_true", help="guarda un snapshot con las métricas actuales")
    ap.add_argument("--render", action="store_true", help="renderiza el dashboard")
    ap.add_argument("--prune", action="store_true", help="conserva solo los últimos 30 snapshots")
    ap.add_argument("--open", action="store_true", help="abrir en el navegador por defecto")
    args = ap.parse_args()

    from evals import history as hist, html_history
    if args.snapshot:
        from evals.comparator import load_cases, load_actuals, run_comparison
        out = run_comparison(load_cases(args.cases), load_actuals(args.cases))
        hist.snapshot(out["metrics"], args.history)
    if args.prune:
        for old in hist.load_history(args.history)[:-30]:
            Path(args.history, f"snapshot-{old['timestamp']}.json").unlink(missing_ok=True)
        hist.update_manifest(args.history)
    if args.render:
        data = hist.load_history(args.history)
        Path(args.out).write_text(html_history.render_dashboard(data), encoding="utf-8")
        print(f"dashboard: {args.out} ({len(data)} snapshots)")
        if args.open:
            import webbrowser
            webbrowser.open(Path(args.out).resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())

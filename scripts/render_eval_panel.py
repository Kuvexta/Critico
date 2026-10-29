"""Render del panel de evals (diseño §14.1): make eval-panel."""
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
    ap = argparse.ArgumentParser(description="Panel HTML de evals")
    ap.add_argument("--out", default="panel-evals.html")
    ap.add_argument("--cases", default=str(BASE / "09_golden_set" / "cases"))
    ap.add_argument("--baseline", default=str(BASE / "09_golden_set" / "baseline" / "v3.4.0.json"))
    ap.add_argument("--open", action="store_true", help="abrir en el navegador por defecto")
    args = ap.parse_args()

    from evals.comparator import load_cases, load_actuals, run_comparison
    from evals.html_report import render_panel
    out = run_comparison(load_cases(args.cases), load_actuals(args.cases),
                         baseline_path=args.baseline)
    html = render_panel(out["metrics"], out["results"], out["dimensions"],
                        out.get("regression"))
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"panel: {args.out}")
    if args.open:
        import webbrowser
        webbrowser.open(Path(args.out).resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())

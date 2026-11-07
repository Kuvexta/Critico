"""CLI del harness de evals (diseño §13.6-13.7): modo offline, regresión, baseline."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # LA-06
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Harness de evals del Crítico (modo offline)")
    ap.add_argument("--mode", choices=["offline", "live"], default="offline")
    ap.add_argument("--cases", default=str(BASE / "09_golden_set" / "cases"))
    ap.add_argument("--baseline", default=str(BASE / "09_golden_set" / "baseline" / "v3.4.0.json"))
    ap.add_argument("--json", action="store_true", help="solo el JSON de métricas")
    ap.add_argument("--fail-on-regression", action="store_true")
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--skill-version", choices=["old", "new"],
                    help="golden set de CONTRATO de la skill (09_golden_set/skill_cases): old = v3.6.0, new = árbol actual")
    ap.add_argument("--expect-all-pass", action="store_true",
                    help="con --skill-version: rc 1 si algún caso no pasa")
    args = ap.parse_args(argv)

    if args.skill_version:
        from evals import skill_contract as sc
        try:
            out = sc.run(args.skill_version)
        except sc.SkillSourceError as error:
            print(f"skill-version {args.skill_version}: {error}", file=sys.stderr)
            return 2
        out["regression"] = sc.regression(out, sc.load_baseline())
        if args.write_baseline:
            sc.write_baseline(out)
            print(f"baseline escrito: {sc.BASELINE}", file=sys.stderr)
        print(json.dumps(out if not args.json else {k: out[k] for k in ("skill_version", "rules", "passed", "total", "regression")},
                         ensure_ascii=False, indent=2))
        if args.fail_on_regression and out["regression"]:
            return 1
        if args.expect_all_pass and out["passed"] != out["total"]:
            return 1
        return 0

    from evals.comparator import load_cases, load_actuals, run_comparison
    if args.mode != "offline":
        print("modo live: pendiente de implementación (el comparador no cambia, diseño §13.6)",
              file=sys.stderr)
        return 2
    cases = load_cases(args.cases)
    actuals = load_actuals(args.cases)
    out = run_comparison(cases, actuals, baseline_path=args.baseline)

    if args.write_baseline:
        b = {"version": "3.4.0", "frozen_at": "2026-10-29",
             "metrics": {"total_cases": len(cases), **out["metrics"]},
             "per_dimension": [{"dimension": d, **v} for d, v in out["dimensions"].items()],
             "thresholds": {"verdict_match_rate": 0.05, "blocker_recall": 0.05,
                            "blocker_precision": 0.05, "audit_trail_coverage": 0.02},
             "thresholds_per_dimension": {"recall": 0.10, "precision": 0.10}}
        Path(args.baseline).write_text(json.dumps(b, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
        print(f"baseline escrito: {args.baseline}")

    if args.json:
        print(json.dumps(out["metrics"], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    if args.fail_on_regression and out.get("regression", {}).get("has_regression"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

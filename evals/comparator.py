"""Comparator del golden set y métricas globales/por-dimensión (diseño §13.4–13.7).

Formato real del golden set (09_golden_set/cases):
- caso: expected {verdict.status, objections[{dimension, severity, claim_contains}],
  audit_trail_min_size, implicit_assumptions_min}
- actual (.actual.yaml): {case_id, verdict.status, objections, audit_trail,
  summary_metrics.implicit_assumptions_discovered}
Blockers/majors = objeciones por severidad; TP/FN/FP por DIMENSIÓN.
"""
from __future__ import annotations
import json
from pathlib import Path

# Tolerancias de regresión (diseño §13.7)
GLOBAL_TOLERANCE = 0.05   # verdict_match_rate, blocker_recall, blocker_precision
TRAIL_TOLERANCE = 0.02    # audit_trail_coverage
DIM_TOLERANCE = 0.10      # precision/recall por dimensión

GLOBAL_METRICS = [
    "verdict_match_rate", "blocker_recall", "blocker_precision",
    "discovery_rate", "audit_trail_coverage",
    "implicit_assumptions_compliance", "skip_incident_rate",
]


def _dims_of(objeciones, severidad: str) -> list[str]:
    """Dimensiones de las objeciones con la severidad dada (dimension puede ser lista)."""
    dims = []
    for o in (objeciones or []):
        if o.get("severity") != severidad:
            continue
        d = o.get("dimension")
        if isinstance(d, list):
            dims.extend(str(x) for x in d)
        elif d is not None:
            dims.append(str(d))
    return sorted(set(dims))


def compare_case(case: dict, actual: dict) -> dict:
    """Compara el .actual.yaml contra el expected del caso."""
    expected = case.get("expected") or {}
    exp_status = (expected.get("verdict") or {}).get("status")
    act_status = (actual.get("verdict") or {}).get("status")
    verdict_match = act_status == exp_status

    exp_blockers = _dims_of(expected.get("objections"), "blocker")
    exp_majors = _dims_of(expected.get("objections"), "major")
    found_blockers = _dims_of(actual.get("objections"), "blocker")
    found_majors = _dims_of(actual.get("objections"), "major")

    trail = actual.get("audit_trail") or []
    min_trail = expected.get("audit_trail_min_size") or 0
    trail_ok = len(trail) >= min_trail
    if exp_status in ("PASA", "PASA_CON_CONDICIONES") and min_trail <= 0:
        trail_ok = len(trail) >= 1  # G2: PASA* exige ≥1 elemento

    sm = actual.get("summary_metrics") or {}
    discovered = int(sm.get("implicit_assumptions_discovered") or 0)
    min_disc = expected.get("implicit_assumptions_min") or 0
    disc_ok = discovered >= min_disc
    skips = int(sm.get("active_skip_incidents") or 0)

    return {
        "case_id": case.get("case_id") or case.get("id"),
        "verdict_match": verdict_match,
        "blockers": {"tp": [d for d in found_blockers if d in exp_blockers],
                     "fn": [d for d in exp_blockers if d not in found_blockers],
                     "fp": [d for d in found_blockers if d not in exp_blockers]},
        "majors": {"tp": [d for d in found_majors if d in exp_majors],
                   "fn": [d for d in exp_majors if d not in found_majors],
                   "fp": [d for d in found_majors if d not in exp_majors]},
        "audit_trail_ok": trail_ok,
        "implicit_assumptions_ok": disc_ok,
        "implicit_assumptions_discovered": discovered,
        "active_skip_incidents": skips,
    }


def global_metrics(results: list[dict]) -> dict:
    """Métricas globales del diseño §13.4. n=0 ⇒ 0.0 honesto (P06, nunca NaN)."""
    n = len(results)
    if n == 0:
        return {k: 0.0 for k in GLOBAL_METRICS}

    def ratio(ok: int, total: int) -> float:
        return round(ok / total, 4) if total else 0.0

    verdict_matches = sum(1 for r in results if r["verdict_match"])
    exp_blockers = sum(len(r["blockers"]["fn"]) + len(r["blockers"]["tp"]) for r in results)
    found_blockers = sum(len(r["blockers"]["tp"]) + len(r["blockers"]["fp"]) for r in results)
    matched_blockers = sum(len(r["blockers"]["tp"]) for r in results)
    trail_ok = sum(1 for r in results if r["audit_trail_ok"])
    disc_ok = sum(1 for r in results if r["implicit_assumptions_ok"])
    skips = sum(r["active_skip_incidents"] for r in results)

    return {
        "verdict_match_rate": ratio(verdict_matches, n),
        "blocker_recall": ratio(matched_blockers, exp_blockers),
        "blocker_precision": ratio(matched_blockers, found_blockers),
        "discovery_rate": round(sum(r["implicit_assumptions_discovered"] for r in results) / n, 4),
        "audit_trail_coverage": ratio(trail_ok, n),
        "implicit_assumptions_compliance": ratio(disc_ok, n),
        "skip_incident_rate": round(skips / n, 4),
    }


def dimension_metrics(results: list[dict]) -> dict:
    """TP/FN/FP, precision, recall y f1 por dimensión (diseño §13.5)."""
    dims: dict[str, dict] = {}
    for r in results:
        for d in r["blockers"]["tp"] + r["blockers"]["fn"] + r["blockers"]["fp"]:
            dims.setdefault(d, {"tp": 0, "fn": 0, "fp": 0})
        for d in r["blockers"]["tp"]:
            dims[d]["tp"] += 1
        for d in r["blockers"]["fn"]:
            dims[d]["fn"] += 1
        for d in r["blockers"]["fp"]:
            dims[d]["fp"] += 1
    out = {}
    for d, v in sorted(dims.items()):
        tp, fn, fp = v["tp"], v["fn"], v["fp"]
        precision = round(tp / (tp + fp), 4) if (tp + fp) else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) else 0.0
        f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) else 0.0
        out[d] = {"tp": tp, "fn": fn, "fp": fp, "precision": precision, "recall": recall, "f1": f1}
    return out


def detect_regression(current: dict, baseline: dict,
                      dims_current: dict | None = None, dims_baseline: dict | None = None) -> dict:
    """Regresión contra baseline con tolerancias (diseño §13.7)."""
    regressions = []
    for m, tol in [("verdict_match_rate", GLOBAL_TOLERANCE),
                   ("blocker_recall", GLOBAL_TOLERANCE),
                   ("blocker_precision", GLOBAL_TOLERANCE)]:
        if current.get(m, 0) < baseline.get(m, 0) - tol:
            regressions.append({"metric": m, "current": current.get(m), "baseline": baseline.get(m)})
    if current.get("audit_trail_coverage", 0) < baseline.get("audit_trail_coverage", 0) - TRAIL_TOLERANCE:
        regressions.append({"metric": "audit_trail_coverage",
                            "current": current.get("audit_trail_coverage"),
                            "baseline": baseline.get("audit_trail_coverage")})
    for dim, bv in (dims_baseline or {}).items():
        cv = (dims_current or {}).get(dim, {})
        for m in ("precision", "recall"):
            if cv.get(m, 0) < bv.get(m, 0) - DIM_TOLERANCE:
                regressions.append({"metric": f"{dim}.{m}", "current": cv.get(m),
                                    "baseline": bv.get(m)})
    return {"regressions": regressions, "has_regression": bool(regressions)}


def load_cases(cases_dir: str | Path) -> list[dict]:
    """Carga los casos del golden set (gc-*.yaml, sin los .actual)."""
    import yaml
    out = []
    for p in sorted(Path(cases_dir).glob("gc-*.yaml")):
        if p.name.endswith(".actual.yaml"):
            continue
        out.append(yaml.safe_load(p.read_text(encoding="utf-8")))
    return out


def load_actuals(cases_dir: str | Path) -> dict[str, dict]:
    """Carga los .actual.yaml pre-grabados por case_id (modo offline)."""
    import yaml
    actuals: dict[str, dict] = {}
    for p in Path(cases_dir).glob("gc-*.actual.yaml"):
        rec = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(rec, dict) and rec.get("case_id"):
            actuals[rec["case_id"]] = rec
    return actuals


def run_comparison(cases: list[dict], actuals: dict[str, dict],
                   baseline_path: str | Path | None = None) -> dict:
    """Pipeline completo: compare → global → dimension → regresión (si baseline)."""
    results = [compare_case(c, actuals.get(c.get("case_id"), {})) for c in cases]
    metrics = global_metrics(results)
    dims = dimension_metrics(results)
    out = {"results": results, "metrics": metrics, "dimensions": dims}
    if baseline_path:
        b = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
        b_metrics = b.get("metrics") or {}
        b_dims = {d["dimension"]: d for d in (b.get("per_dimension") or [])}
        out["regression"] = detect_regression(metrics, b_metrics, dims, b_dims)
    return out

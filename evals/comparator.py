"""Comparator del golden set y métricas globales/por-dimensión (diseño §13.4–13.7).

Métricas globales: verdict_match_rate, blocker_recall, blocker_precision,
discovery_rate, audit_trail_coverage, implicit_assumptions_compliance,
skip_incident_rate. Por dimensión: TP/FN/FP, precision, recall, f1.
Detección de regresión contra baseline con tolerancias declaradas.
"""
from __future__ import annotations
import json
from pathlib import Path

MIN_DISCOVERED = 2  # supuestos mínimos por caso (implicit_assumptions_compliance)

# Tolerancias de regresión (diseño §13.7)
GLOBAL_TOLERANCE = 0.05   # verdict_match_rate, blocker_recall, blocker_precision
TRAIL_TOLERANCE = 0.02    # audit_trail_coverage
DIM_TOLERANCE = 0.10      # precision/recall por dimensión

GLOBAL_METRICS = [
    "verdict_match_rate", "blocker_recall", "blocker_precision",
    "discovery_rate", "audit_trail_coverage",
    "implicit_assumptions_compliance", "skip_incident_rate",
]


def _as_list(value) -> list:
    return list(value or [])


def compare_case(case: dict, actual: dict) -> dict:
    """Compara un caso real contra el esperado del golden set."""
    expected = case.get("expected") or {}
    sm = actual.get("summary_metrics") or {}
    verdict_match = actual.get("status") == expected.get("status")

    exp_blockers = _as_list(expected.get("blockers"))
    exp_majors = _as_list(expected.get("majors"))
    found_blockers = _as_list(sm.get("blockers"))
    found_majors = _as_list(sm.get("majors"))

    blockers_tp = [b for b in found_blockers if b in exp_blockers]
    blockers_fn = [b for b in exp_blockers if b not in found_blockers]
    blockers_fp = [b for b in found_blockers if b not in exp_blockers]
    majors_tp = [m for m in found_majors if m in exp_majors]
    majors_fn = [m for m in exp_majors if m not in found_majors]
    majors_fp = [m for m in found_majors if m not in exp_majors]

    trail = actual.get("audit_trail_passed_checks") or []
    trail_ok = len(trail) >= 1 if expected.get("status") in ("PASA", "PASA_CON_CONDICIONES") else True
    discovered = int(sm.get("implicit_assumptions_discovered") or 0)
    skips = int(sm.get("active_skip_incidents") or 0)

    return {
        "case_id": case.get("id"),
        "verdict_match": verdict_match,
        "blockers": {"tp": blockers_tp, "fn": blockers_fn, "fp": blockers_fp},
        "majors": {"tp": majors_tp, "fn": majors_fn, "fp": majors_fp},
        "audit_trail_ok": trail_ok,
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
    compliant = sum(1 for r in results if r["implicit_assumptions_discovered"] >= MIN_DISCOVERED)
    skips = sum(r["active_skip_incidents"] for r in results)

    return {
        "verdict_match_rate": ratio(verdict_matches, n),
        "blocker_recall": ratio(matched_blockers, exp_blockers),
        "blocker_precision": ratio(matched_blockers, found_blockers),
        "discovery_rate": round(sum(r["implicit_assumptions_discovered"] for r in results) / n, 4),
        "audit_trail_coverage": ratio(trail_ok, n),
        "implicit_assumptions_compliance": ratio(compliant, n),
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


def run_comparison(cases: list[dict], actuals: dict[str, dict]) -> dict:
    """Pipeline completo: compare → global → dimension → regression (si baseline)."""
    results = [compare_case(c, actuals.get(c.get("id"), {})) for c in cases]
    metrics = global_metrics(results)
    dims = dimension_metrics(results)
    out = {"results": results, "metrics": metrics, "dimensions": dims}
    return out


def load_actuals(dir_path: str | Path) -> dict[str, dict]:
    """Carga los .actual.yaml pre-grabados por id de caso (modo offline)."""
    actuals: dict[str, dict] = {}
    for p in Path(dir_path).rglob("*.actual.yaml"):
        import yaml
        rec = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(rec, dict) and rec.get("artifact_id"):
            actuals[str(p.stem).replace(".actual", "")] = rec
    return actuals

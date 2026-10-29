"""Comparator + métricas globales + por-dimensión (23 tests, formato real del golden set)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from evals.comparator import (  # noqa: E402
    compare_case, global_metrics, dimension_metrics, detect_regression, GLOBAL_METRICS,
)


def _case(**over) -> dict:
    d = {"case_id": "GC-001",
         "expected": {"verdict": {"state_class": "TERMINAL", "status": "PASA", "reason_code": None},
                      "objections": [], "audit_trail_min_size": 1, "implicit_assumptions_min": 2}}
    d.update(over)
    return d


def _actual(status="PASA", objections=None, trail=1, discovered=2) -> dict:
    return {"case_id": "GC-001",
            "verdict": {"state_class": "TERMINAL", "status": status, "reason_code": None},
            "objections": objections or [],
            "audit_trail": [{"assumption": f"a{i}"} for i in range(trail)],
            "summary_metrics": {"implicit_assumptions_discovered": discovered,
                                "blockers_count": 0, "majors_count": 0,
                                "active_accepted_risks": [], "budget_consumed_pct": 10.0,
                                "active_skip_incidents": 0, "skip_incident_ids": []}}


def _exp(status, blockers=(), majors=(), trail=1, disc=2) -> dict:
    objs = ([{"dimension": d, "severity": "blocker"} for d in blockers]
            + [{"dimension": d, "severity": "major"} for d in majors])
    return {"verdict": {"state_class": "TERMINAL", "status": status, "reason_code": None},
            "objections": objs, "audit_trail_min_size": trail, "implicit_assumptions_min": disc}


def test_01_verdict_match_verdadero():
    r = compare_case(_case(), _actual())
    assert r["verdict_match"] is True


def test_02_verdict_match_falso():
    r = compare_case(_case(expected=_exp("NO_PASA")), _actual())
    assert r["verdict_match"] is False


def test_03_blocker_tp():
    r = compare_case(_case(expected=_exp("NO_PASA", blockers=["24"])),
                     _actual(status="NO_PASA", objections=[{"dimension": "24", "severity": "blocker"}]))
    assert r["blockers"]["tp"] == ["24"]


def test_04_blocker_fn():
    r = compare_case(_case(expected=_exp("NO_PASA", blockers=["24"])),
                     _actual(status="NO_PASA"))
    assert r["blockers"]["fn"] == ["24"]


def test_05_blocker_fp():
    r = compare_case(_case(expected=_exp("NO_PASA")),
                     _actual(status="NO_PASA", objections=[{"dimension": "30", "severity": "blocker"}]))
    assert r["blockers"]["fp"] == ["30"]


def test_06_major_tp():
    r = compare_case(_case(expected=_exp("NO_PASA", majors=["51"])),
                     _actual(status="NO_PASA", objections=[{"dimension": "51", "severity": "major"}]))
    assert r["majors"]["tp"] == ["51"]


def test_07_audit_trail_requerido_en_pasa():
    r = compare_case(_case(), _actual(trail=0))
    assert r["audit_trail_ok"] is False


def test_08_audit_trail_no_requerido_en_no_pasa():
    r = compare_case(_case(expected=_exp("NO_PASA", trail=0)), _actual(status="NO_PASA", trail=0))
    assert r["audit_trail_ok"] is True


def test_09_captura_supuestos_descubiertos():
    r = compare_case(_case(), _actual(discovered=3))
    assert r["implicit_assumptions_discovered"] == 3


def test_10_compliance_por_minimo_del_caso():
    r = compare_case(_case(expected=_exp("PASA", disc=3)), _actual(discovered=2))
    assert r["implicit_assumptions_ok"] is False


def test_11_verdict_match_rate_exacto():
    results = [compare_case(_case(case_id="A"), _actual()),
               compare_case(_case(case_id="B", expected=_exp("NO_PASA")), _actual())]
    assert global_metrics(results)["verdict_match_rate"] == 0.5


def test_12_blocker_recall():
    results = [compare_case(_case(expected=_exp("NO_PASA", blockers=["24"])),
                            _actual(status="NO_PASA", objections=[{"dimension": "24", "severity": "blocker"}]))]
    assert global_metrics(results)["blocker_recall"] == 1.0


def test_13_blocker_precision_con_fp():
    results = [compare_case(_case(expected=_exp("NO_PASA", blockers=["24"])),
                            _actual(status="NO_PASA", objections=[{"dimension": "24", "severity": "blocker"},
                                                                  {"dimension": "30", "severity": "blocker"}]))]
    assert global_metrics(results)["blocker_precision"] == 0.5


def test_14_discovery_rate_es_la_media():
    results = [compare_case(_case(case_id="A"), _actual(discovered=4)),
               compare_case(_case(case_id="B"), _actual(discovered=0))]
    assert global_metrics(results)["discovery_rate"] == 2.0


def test_15_audit_trail_coverage():
    results = [compare_case(_case(case_id="A"), _actual()),
               compare_case(_case(case_id="B"), _actual(trail=0))]
    assert global_metrics(results)["audit_trail_coverage"] == 0.5


def test_16_compliance_global():
    results = [compare_case(_case(case_id="A", expected=_exp("PASA", disc=2)), _actual(discovered=2)),
               compare_case(_case(case_id="B", expected=_exp("PASA", disc=2)), _actual(discovered=1))]
    assert global_metrics(results)["implicit_assumptions_compliance"] == 0.5


def test_17_skip_incident_rate():
    a = _actual()
    a["summary_metrics"]["active_skip_incidents"] = 1
    results = [compare_case(_case(case_id="A"), a),
               compare_case(_case(case_id="B"), _actual())]
    assert global_metrics(results)["skip_incident_rate"] == 0.5


def test_18_sin_casos_no_hay_nan():
    m = global_metrics([])
    assert all(isinstance(v, (int, float)) for v in m.values())
    assert m["verdict_match_rate"] == 0.0


def test_19_dimensiones_tp_fn_fp():
    results = [compare_case(_case(expected=_exp("NO_PASA", blockers=["24", "30"])),
                            _actual(status="NO_PASA", objections=[{"dimension": "24", "severity": "blocker"},
                                                                  {"dimension": "51", "severity": "blocker"}]))]
    dims = dimension_metrics(results)
    assert dims["24"]["tp"] == 1 and dims["30"]["fn"] == 1 and dims["51"]["fp"] == 1


def test_20_precision_cero_para_falsos_positivos():
    results = [compare_case(_case(expected=_exp("NO_PASA", blockers=["24"])),
                            _actual(status="NO_PASA", objections=[{"dimension": "24", "severity": "blocker"},
                                                                  {"dimension": "30", "severity": "blocker"}]))]
    dims = dimension_metrics(results)
    assert dims["24"]["precision"] == 1.0
    assert dims["30"]["precision"] == 0.0


def test_21_recall_y_f1():
    results = [compare_case(_case(expected=_exp("NO_PASA", blockers=["24"])),
                            _actual(status="NO_PASA"))]
    d = dimension_metrics(results)["24"]
    assert d["recall"] == 0.0 and d["f1"] == 0.0


def test_22_regresion_global_por_encima_de_tolerancia():
    current = {**{k: 1.0 for k in GLOBAL_METRICS}, "verdict_match_rate": 0.80}
    baseline = {**{k: 1.0 for k in GLOBAL_METRICS}}
    r = detect_regression(current, baseline)
    assert r["has_regression"], "0.80 < 1.0 - 0.05 debería marcar regresión"


def test_23_regresion_por_dimension_dentro_de_tolerancia_no_marca():
    current = {k: 1.0 for k in GLOBAL_METRICS}
    baseline = {k: 1.0 for k in GLOBAL_METRICS}
    r = detect_regression(current, baseline,
                          dims_current={"24": {"precision": 0.92, "recall": 0.95}},
                          dims_baseline={"24": {"precision": 1.0, "recall": 1.0}})
    assert not r["has_regression"], "0.92 está dentro de la tolerancia de -10%"

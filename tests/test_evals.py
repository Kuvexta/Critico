"""Comparator + métricas globales + por-dimensión (23 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_verdict  # noqa: E402
from evals.comparator import (  # noqa: E402
    compare_case, global_metrics, dimension_metrics, detect_regression, GLOBAL_METRICS,
)


def _case(**over) -> dict:
    d = {"id": "GC-001", "expected": {"status": "PASA", "blockers": [], "majors": []}}
    d.update(over)
    return d


def _actual(**over) -> dict:
    v = base_verdict()
    sm = v["summary_metrics"]
    sm["blockers"] = []
    sm["majors"] = []
    v.update(over)
    return v


def test_01_verdict_match_verdadero():
    r = compare_case(_case(), _actual(status="PASA"))
    assert r["verdict_match"] is True


def test_02_verdict_match_falso():
    r = compare_case(_case(expected={"status": "NO_PASA", "blockers": [], "majors": []}),
                     _actual(status="PASA"))
    assert r["verdict_match"] is False


def test_03_blocker_tp():
    r = compare_case(_case(expected={"status": "NO_PASA", "blockers": ["24"], "majors": []}),
                     _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                             "blockers": ["24"], "majors": []}))
    assert r["blockers"]["tp"] == ["24"]


def test_04_blocker_fn():
    r = compare_case(_case(expected={"status": "NO_PASA", "blockers": ["24"], "majors": []}),
                     _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                             "blockers": [], "majors": []}))
    assert r["blockers"]["fn"] == ["24"]


def test_05_blocker_fp():
    r = compare_case(_case(expected={"status": "NO_PASA", "blockers": [], "majors": []}),
                     _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                             "blockers": ["30"], "majors": []}))
    assert r["blockers"]["fp"] == ["30"]


def test_06_major_tp():
    r = compare_case(_case(expected={"status": "NO_PASA", "blockers": [], "majors": ["51"]}),
                     _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                             "blockers": [], "majors": ["51"]}))
    assert r["majors"]["tp"] == ["51"]


def test_07_audit_trail_requerido_en_pasa():
    v = _actual(status="PASA")
    v["audit_trail_passed_checks"] = []
    r = compare_case(_case(), v)
    assert r["audit_trail_ok"] is False


def test_08_audit_trail_no_requerido_en_no_pasa():
    v = _actual(status="NO_PASA")
    v["audit_trail_passed_checks"] = []
    r = compare_case(_case(expected={"status": "NO_PASA", "blockers": [], "majors": []}), v)
    assert r["audit_trail_ok"] is True


def test_09_captura_supuestos_descubiertos():
    v = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": []})
    r = compare_case(_case(), v)
    assert r["implicit_assumptions_discovered"] == 2


def test_10_captura_skips_activos():
    v = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": [],
                                 "active_skip_incidents": 1})
    r = compare_case(_case(), v)
    assert r["active_skip_incidents"] == 1


def test_11_verdict_match_rate_exacto():
    results = [compare_case(_case(id="A"), _actual(status="PASA")),
               compare_case(_case(id="B", expected={"status": "NO_PASA", "blockers": [], "majors": []}),
                            _actual(status="PASA"))]
    assert global_metrics(results)["verdict_match_rate"] == 0.5


def test_12_blocker_recall():
    results = [compare_case(_case(id="A", expected={"status": "NO_PASA", "blockers": ["24"], "majors": []}),
                            _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                                    "blockers": ["24"], "majors": []}))]
    assert global_metrics(results)["blocker_recall"] == 1.0


def test_13_blocker_precision_con_fp():
    results = [compare_case(_case(id="A", expected={"status": "NO_PASA", "blockers": ["24"], "majors": []}),
                            _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                                    "blockers": ["24", "30"], "majors": []}))]
    assert global_metrics(results)["blocker_precision"] == 0.5


def test_14_discovery_rate_es_la_media():
    v1 = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": [],
                                  "implicit_assumptions_discovered": 4})
    v2 = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": [],
                                  "implicit_assumptions_discovered": 0})
    results = [compare_case(_case(id="A"), v1), compare_case(_case(id="B"), v2)]
    assert global_metrics(results)["discovery_rate"] == 2.0


def test_15_audit_trail_coverage():
    v1 = _actual(status="PASA")
    v2 = _actual(status="PASA")
    v2["audit_trail_passed_checks"] = []
    results = [compare_case(_case(id="A"), v1), compare_case(_case(id="B"), v2)]
    assert global_metrics(results)["audit_trail_coverage"] == 0.5


def test_16_compliance_usa_el_umbral_de_2():
    v1 = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": [],
                                  "implicit_assumptions_discovered": 2})
    v2 = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": [],
                                  "implicit_assumptions_discovered": 1})
    results = [compare_case(_case(id="A"), v1), compare_case(_case(id="B"), v2)]
    assert global_metrics(results)["implicit_assumptions_compliance"] == 0.5


def test_17_skip_incident_rate():
    v = _actual(summary_metrics={**base_verdict()["summary_metrics"], "blockers": [], "majors": [],
                                 "active_skip_incidents": 1})
    results = [compare_case(_case(id="A"), v), compare_case(_case(id="B"), _actual())]
    assert global_metrics(results)["skip_incident_rate"] == 0.5


def test_18_sin_casos_no_hay_nan():
    m = global_metrics([])
    assert all(isinstance(v, (int, float)) for v in m.values())
    assert m["verdict_match_rate"] == 0.0


def test_19_dimensiones_tp_fn_fp():
    results = [compare_case(_case(id="A", expected={"status": "NO_PASA", "blockers": ["24", "30"], "majors": []}),
                            _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                                    "blockers": ["24", "51"], "majors": []}))]
    dims = dimension_metrics(results)
    assert dims["24"] == {"tp": 1, "fn": 0, "fp": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0}
    assert dims["30"]["fn"] == 1
    assert dims["51"]["fp"] == 1


def test_20_precision_cero_para_falsos_positivos():
    results = [compare_case(_case(id="A", expected={"status": "NO_PASA", "blockers": ["24"], "majors": []}),
                            _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                                    "blockers": ["24", "30"], "majors": []}))]
    dims = dimension_metrics(results)
    assert dims["24"]["precision"] == 1.0
    assert dims["30"]["precision"] == 0.0  # FP puro: TP=0


def test_21_recall_y_f1():
    results = [compare_case(_case(id="A", expected={"status": "NO_PASA", "blockers": ["24"], "majors": []}),
                            _actual(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                                    "blockers": [], "majors": []}))]
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

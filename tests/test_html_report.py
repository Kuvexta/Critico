"""Panel HTML: self-contained, WCAG AA, print, sección de skip incidents (11 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from evals.html_report import render_panel  # noqa: E402


def _ok_metrics() -> dict:
    return {"verdict_match_rate": 1.0, "blocker_recall": 1.0, "blocker_precision": 1.0,
            "discovery_rate": 2.0, "audit_trail_coverage": 1.0,
            "implicit_assumptions_compliance": 1.0, "skip_incident_rate": 0.0}


def _results(ok: bool = True, skips: int = 0) -> list:
    return [{"case_id": "GC-001", "verdict_match": ok, "blockers": {"tp": [], "fn": [], "fp": []},
             "audit_trail_ok": ok, "implicit_assumptions_discovered": 2,
             "active_skip_incidents": skips}]


def test_01_salida_es_html_con_doctype():
    html = render_panel(_ok_metrics(), _results(), {})
    assert html.startswith("<!DOCTYPE html>")


def test_02_banner_ok_cuando_todo_coincide():
    html = render_panel(_ok_metrics(), _results(), {})
    assert "banner-ok" in html and "OK" in html


def test_03_banner_fail_con_desajuste():
    html = render_panel(_ok_metrics(), _results(ok=False), {})
    assert "banner-fail" in html


def test_04_tabla_de_casos_con_id():
    html = render_panel(_ok_metrics(), _results(), {})
    assert "GC-001" in html and "Casos" in html


def test_05_seccion_de_skips_cuando_hay_activos():
    m = _ok_metrics()
    m["skip_incident_rate"] = 1.0
    html = render_panel(m, _results(skips=1), {})
    assert "skip-incidents" in html


def test_06_banner_con_la_regla_de_no_pasa_en_skips():
    m = _ok_metrics()
    m["skip_incident_rate"] = 1.0
    html = render_panel(m, _results(skips=1), {})
    assert "NO_PASA" in html


def test_07_sin_skips_no_hay_seccion():
    html = render_panel(_ok_metrics(), _results(), {})
    assert "skip-incidents" not in html


def test_08_kpis_presentes():
    html = render_panel(_ok_metrics(), _results(), {})
    for kpi in ["Verdict match", "Blocker recall", "Blocker precision", "Discovery"]:
        assert kpi in html


def test_09_sin_js_ni_cdn():
    html = render_panel(_ok_metrics(), _results(), {})
    assert "<script" not in html
    assert "http://" not in html and "https://" not in html


def test_10_accesible_con_aria_y_roles():
    html = render_panel(_ok_metrics(), _results(), {})
    assert "role=" in html and "aria-label" in html


def test_11_print_friendly_y_barras_svg():
    html = render_panel(_ok_metrics(), _results(), {"24": {"tp": 1, "fn": 0, "fp": 0,
                                                            "precision": 1.0, "recall": 1.0, "f1": 1.0}})
    assert "@media print" in html
    assert "<svg" in html

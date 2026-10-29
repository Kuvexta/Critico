"""M-A a M-F: mejoras v3.4 (16 tests = 2 + 3 + 2 + 2 + 3 + 4)."""
import sys
import yaml
from pathlib import Path
from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_objection, base_triage  # noqa: E402

OBJ = yaml.safe_load((BASE / "05_schema/objection.yaml").read_text(encoding="utf-8"))
TRI = yaml.safe_load((BASE / "05_schema/triage.yaml").read_text(encoding="utf-8"))
CONFIG = yaml.safe_load((BASE / "04_critic.config.yaml").read_text(encoding="utf-8"))
INTEG = CONFIG.get("integration") or {}


# ---- M-A: v1_angle en la bitácora (2) ----
def test_ma_01_objection_acepta_v1_angle():
    o = base_objection(v1_angle=[8])
    assert not list(Draft202012Validator(OBJ).iter_errors(o))


def test_ma_02_v1_angle_fuera_de_rango_falla():
    o = base_objection(v1_angle=[12])
    assert list(Draft202012Validator(OBJ).iter_errors(o))


# ---- M-B: plan_status agregado (3) ----
def test_mb_01_triage_acepta_plan_status():
    t = base_triage(plan_status={"parent_id": "ART-PADRE", "total_steps": 5,
                                 "steps_passed": 1, "steps_blocked": 1,
                                 "steps_pending": 3, "blocked_at_step": 2,
                                 "plan_verdict": "blocked"})
    assert not list(Draft202012Validator(TRI).iter_errors(t))


def test_mb_02_plan_verdict_enum_valido():
    t = base_triage(plan_status={"parent_id": "ART-PADRE", "total_steps": 5,
                                 "steps_passed": 1, "steps_blocked": 1,
                                 "steps_pending": 3, "blocked_at_step": 2,
                                 "plan_verdict": "en_otra_cosa"})
    assert list(Draft202012Validator(TRI).iter_errors(t))


def test_mb_03_plan_bloqueado_usa_reason_plan_blocked():
    verd = yaml.safe_load((BASE / "05_schema/verdict.yaml").read_text(encoding="utf-8"))
    assert "PLAN_BLOCKED" in verd["properties"]["reason_code"]["enum"]


# ---- M-C: contrato de check_encargo (2) ----
def test_mc_01_contrato_check_encargo_documentado():
    cc = INTEG.get("check_encargo_contract") or {}
    for k in ["input", "output", "invocation"]:
        assert k in cc, f"check_encargo_contract sin {k}"


def test_mc_02_salida_por_gate_faltante_es_skip_incident():
    cc = INTEG.get("check_encargo_contract") or {}
    assert "skip_incident" in str(cc.get("output", "")).lower()


# ---- M-D: rotación de modelos (2) ----
def test_md_01_model_rotation_declarado_como_politica():
    mr = INTEG.get("model_rotation") or {}
    assert mr.get("enabled") is False


def test_md_02_prohibiciones_de_rotacion():
    mr = INTEG.get("model_rotation") or {}
    prohibitions = str(mr)
    assert "author_and_reviewer" in prohibitions and "reviewer_and_verifier" in prohibitions


# ---- M-E: panel muestra skip incidents (3) ----
def test_me_01_seccion_de_skips_cuando_hay_activos():
    from evals.html_report import render_panel
    m = {"verdict_match_rate": 1.0, "blocker_recall": 1.0, "blocker_precision": 1.0,
         "discovery_rate": 2.0, "audit_trail_coverage": 1.0,
         "implicit_assumptions_compliance": 1.0, "skip_incident_rate": 1.0}
    html = render_panel(m, [{"case_id": "GC-001", "verdict_match": False,
                             "blockers": {"tp": [], "fn": [], "fp": []},
                             "audit_trail_ok": False, "implicit_assumptions_discovered": 0,
                             "active_skip_incidents": 1}], {})
    assert "skip-incidents" in html


def test_me_02_banner_con_regla_no_pasa():
    from evals.html_report import render_panel
    m = {"verdict_match_rate": 1.0, "blocker_recall": 1.0, "blocker_precision": 1.0,
         "discovery_rate": 2.0, "audit_trail_coverage": 1.0,
         "implicit_assumptions_compliance": 1.0, "skip_incident_rate": 1.0}
    html = render_panel(m, [{"case_id": "GC-001", "verdict_match": True,
                             "blockers": {"tp": [], "fn": [], "fp": []},
                             "audit_trail_ok": True, "implicit_assumptions_discovered": 2,
                             "active_skip_incidents": 1}], {})
    assert "NO_PASA" in html


def test_me_03_sin_skips_no_hay_seccion():
    from evals.html_report import render_panel
    m = {"verdict_match_rate": 1.0, "blocker_recall": 1.0, "blocker_precision": 1.0,
         "discovery_rate": 2.0, "audit_trail_coverage": 1.0,
         "implicit_assumptions_compliance": 1.0, "skip_incident_rate": 0.0}
    html = render_panel(m, [{"case_id": "GC-001", "verdict_match": True,
                             "blockers": {"tp": [], "fn": [], "fp": []},
                             "audit_trail_ok": True, "implicit_assumptions_discovered": 2,
                             "active_skip_incidents": 0}], {})
    assert "skip-incidents" not in html


# ---- M-F: dashboard con skip rate (4) ----
def test_mf_01_trend_metrics_incluye_skip_incident_rate():
    from evals import history
    assert "skip_incident_rate" in history.TREND_METRICS


def test_mf_02_flecha_invertida_para_skip_rate():
    from evals import history
    h = [{"metrics": {"skip_incident_rate": v}} for v in [0.5, 0.2]]
    assert history.trend_direction(h, "skip_incident_rate")["direction"] == "improving"


def test_mf_03_dashboard_incluye_sparklines():
    from evals import html_history, history
    h = [{"timestamp": "20261029T000000Z", "sha256": "a" * 64,
          "metrics": {"skip_incident_rate": 0.2, "verdict_match_rate": 1.0,
                      "blocker_recall": 1.0, "blocker_precision": 1.0,
                      "discovery_rate": 2.0, "audit_trail_coverage": 1.0,
                      "implicit_assumptions_compliance": 1.0}}]
    html = html_history.render_dashboard(h)
    assert "<polyline" in html


def test_mf_04_snapshot_persiste_skip_rate(tmp_path):
    from evals import history
    rec = history.snapshot({"skip_incident_rate": 0.25, "verdict_match_rate": 1.0}, tmp_path)
    assert rec["metrics"]["skip_incident_rate"] == 0.25

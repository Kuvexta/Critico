"""I3: registro explícito de SKIP_INCIDENT (5 tests)."""
import sys
import yaml
from pathlib import Path
from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_verdict  # noqa: E402
from evals.validators import validate_verdict_invariants  # noqa: E402

SKIP = yaml.safe_load((BASE / "05_schema/skip_incident.yaml").read_text(encoding="utf-8"))
VERD = yaml.safe_load((BASE / "05_schema/verdict.yaml").read_text(encoding="utf-8"))


def _skip() -> dict:
    return {"incident_id": "SKP-" + "a" * 12, "artifact_id": "ART-0001",
            "expected_gate": "GATE_B", "detected_by": "check_encargo_v2",
            "detected_at": "2026-10-29T00:00:00Z", "severity": "major",
            "policy_ref": "P21"}


def test_01_skip_incident_valido_aceptado():
    assert not list(Draft202012Validator(SKIP).iter_errors(_skip()))


def test_02_con_skip_activo_pasa_es_violacion():
    v = base_verdict(status="PASA", summary_metrics={**base_verdict()["summary_metrics"],
                       "active_skip_incidents": 1, "skip_incident_ids": ["SKP-" + "a" * 12]})
    assert validate_verdict_invariants(v), "I3: un artefacto con SKIP_INCIDENT no puede recibir PASA"


def test_03_con_skip_no_pasa_y_gate_skipped_es_valido():
    v = base_verdict(status="NO_PASA", reason_code="GATE_SKIPPED",
                     summary_metrics={**base_verdict()["summary_metrics"],
                                      "active_skip_incidents": 1,
                                      "skip_incident_ids": ["SKP-" + "a" * 12]})
    assert validate_verdict_invariants(v) == []


def test_04_skip_activo_sin_gate_skipped_es_violacion():
    v = base_verdict(status="NO_PASA", reason_code=None,
                     summary_metrics={**base_verdict()["summary_metrics"],
                                      "active_skip_incidents": 1,
                                      "skip_incident_ids": ["SKP-" + "a" * 12]})
    assert validate_verdict_invariants(v)


def test_05_verdict_declara_skips_en_summary_metrics():
    v = base_verdict(summary_metrics={**base_verdict()["summary_metrics"],
                                      "active_skip_incidents": 1,
                                      "skip_incident_ids": ["SKP-" + "a" * 12]})
    assert not list(Draft202012Validator(VERD).iter_errors(v))

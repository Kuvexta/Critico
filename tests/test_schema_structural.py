"""Estructura JSON-Schema: los 8 esquemas congelados son válidos y exigentes (15 tests)."""
import yaml
from pathlib import Path
from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parents[1]
NAMES = ["objection", "triage", "verdict", "outcome", "pattern",
         "risk_accepted", "skip_incident", "golden_case"]


def _schema(name) -> dict:
    return yaml.safe_load((BASE / "05_schema" / f"{name}.yaml").read_text(encoding="utf-8"))


def _required(name) -> list:
    return _schema(name).get("required") or []


def test_01_son_exactamente_8_esquemas():
    files = sorted(p.name for p in (BASE / "05_schema").glob("*.yaml"))
    assert files == sorted(n + ".yaml" for n in NAMES)


def test_02_objetcion_schema_valido():
    Draft202012Validator.check_schema(_schema("objection"))


def test_03_triage_schema_valido():
    Draft202012Validator.check_schema(_schema("triage"))


def test_04_verdict_schema_valido():
    Draft202012Validator.check_schema(_schema("verdict"))


def test_05_outcome_schema_valido():
    Draft202012Validator.check_schema(_schema("outcome"))


def test_06_pattern_schema_valido():
    Draft202012Validator.check_schema(_schema("pattern"))


def test_07_risk_accepted_schema_valido():
    Draft202012Validator.check_schema(_schema("risk_accepted"))


def test_08_skip_incident_schema_valido():
    Draft202012Validator.check_schema(_schema("skip_incident"))


def test_09_golden_case_schema_valido():
    Draft202012Validator.check_schema(_schema("golden_case"))


def test_10_objection_exige_lo_esencial():
    r = _required("objection")
    for k in ["objection_id", "artifact_id", "dimension", "severity", "provenance"]:
        assert k in r


def test_11_triage_exige_resumen_de_dimensiones():
    r = _required("triage")
    for k in ["triage_id", "artifact_id", "profiles", "dimensions_summary",
              "active_dimensions", "triage_overrides"]:
        assert k in r


def test_12_verdict_exige_maquina_de_estados():
    r = _required("verdict")
    for k in ["verdict_id", "artifact_id", "gate", "state_class", "status"]:
        assert k in r


def test_13_skip_incident_exige_gate_esperado():
    r = _required("skip_incident")
    for k in ["incident_id", "artifact_id", "expected_gate", "detected_by"]:
        assert k in r


def test_14_golden_case_exige_ground_truth():
    r = _required("golden_case")
    for k in ["case_id", "artifact", "triage", "expected", "ground_truth"]:
        assert k in r


def test_15_todos_declaran_draft_2020_12():
    for n in NAMES:
        assert _schema(n).get("$schema", "").endswith("draft/2020-12/schema")

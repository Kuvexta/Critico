"""G1 · G1-bis · G2: enforcement condicional del veredicto (12 tests)."""
import sys
import yaml
from pathlib import Path
from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_verdict  # noqa: E402

SCHEMA = yaml.safe_load((BASE / "05_schema/verdict.yaml").read_text(encoding="utf-8"))
V = Draft202012Validator(SCHEMA)


def _errors(v) -> list:
    return list(V.iter_errors(v))


def test_g1_01_suspension_sin_control_es_invalida():
    v = base_verdict(status="NECESITA_INFO", state_class="OPERATIONAL_SUSPENSION",
                     suspension_control=None)
    assert _errors(v), "G1: OPERATIONAL_SUSPENSION exige suspension_control"


def test_g1_02_suspension_con_control_es_valida():
    v = base_verdict(status="NECESITA_INFO", state_class="OPERATIONAL_SUSPENSION",
                     suspension_control={"cycle_count": 1, "max_cycles": 2, "timeout_hours": 24,
                                         "target": "author", "suspension_reason": "MISSING_INFO",
                                         "missing_info_questions": ["¿detalle?"],
                                         "unreviewed_dimensions": ["24"]})
    assert not _errors(v)


def test_g1bis_03_terminal_con_control_es_invalida():
    v = base_verdict(status="NO_PASA", state_class="TERMINAL",
                     suspension_control={"cycle_count": 1, "max_cycles": 2, "timeout_hours": 24,
                                         "target": "author", "suspension_reason": "MISSING_INFO",
                                         "missing_info_questions": ["¿?"],
                                         "unreviewed_dimensions": ["24"]})
    assert _errors(v), "G1-bis: TERMINAL exige suspension_control null"


def test_g1bis_04_terminal_sin_control_es_valida():
    v = base_verdict(status="NO_PASA", state_class="TERMINAL", suspension_control=None)
    assert not _errors(v)


def test_g2_05_pasa_exige_audit_trail():
    v = base_verdict(status="PASA", audit_trail_passed_checks=[])
    assert _errors(v), "G2: PASA exige audit_trail con ≥1 elemento"


def test_g2_06_pasa_con_trail_es_valida():
    v = base_verdict(status="PASA")
    assert not _errors(v)


def test_g2_07_pasa_con_condiciones_exige_audit_trail():
    v = base_verdict(status="PASA_CON_CONDICIONES", audit_trail_passed_checks=[])
    assert _errors(v)


def test_g2_08_no_pasa_sin_trail_es_valida():
    v = base_verdict(status="NO_PASA", audit_trail_passed_checks=[])
    assert not _errors(v)


def test_g2_09_elemento_del_trail_exige_los_cinco_campos():
    v = base_verdict(audit_trail_passed_checks=[{"assumption": "x"}])
    assert _errors(v), "cada elemento exige assumption/dimension/attack_vector/resistance_evidence/confidence"


def test_g2_10_confidence_fuera_de_rango_es_invalida():
    v = base_verdict(audit_trail_passed_checks=[
        {"assumption": "x", "dimension": "24", "attack_vector": "y",
         "resistance_evidence": "z", "confidence": 1.7}])
    assert _errors(v)


def test_g2_11_confidence_entre_0_y_1_es_valida():
    v = base_verdict(audit_trail_passed_checks=[
        {"assumption": "x", "dimension": "24", "attack_vector": "y",
         "resistance_evidence": "z", "confidence": 0.5}])
    assert not _errors(v)


def test_g2_12_trail_dimension_debe_ser_string():
    v = base_verdict(audit_trail_passed_checks=[
        {"assumption": "x", "dimension": 24, "attack_vector": "y",
         "resistance_evidence": "z", "confidence": 0.5}])
    assert _errors(v), "dimensión como número debe fallar el tipo del schema"

"""M2/M3/R1: máquina de estados del veredicto (10 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_verdict  # noqa: E402
from evals.validators import validate_verdict_invariants  # noqa: E402


def test_m3_01_reset_con_doble_condicion_es_valido():
    v = base_verdict(status="NO_PASA", summary_metrics={**base_verdict()["summary_metrics"],
                       "suspension_cycles_reset_reason": "artifact_hash_change_and_questions_resolved"})
    assert validate_verdict_invariants(v) == []


def test_m3_02_reset_con_motivo_invalido_es_violacion():
    v = base_verdict(summary_metrics={**base_verdict()["summary_metrics"],
                       "suspension_cycles_reset_reason": "porque_si"})
    assert validate_verdict_invariants(v)


def test_m3_03_reset_declarado_sin_motivo_es_violacion():
    v = base_verdict(summary_metrics={**base_verdict()["summary_metrics"], "reset_of_suspension": True})
    assert validate_verdict_invariants(v)


def test_m3_04_sin_reset_es_valido():
    v = base_verdict()
    assert validate_verdict_invariants(v) == []


def test_r1_05_necesita_info_implica_suspension_operacional():
    v = base_verdict(status="NECESITA_INFO", state_class="TERMINAL")
    assert validate_verdict_invariants(v)


def test_r1_06_revision_parcial_implica_suspension_operacional():
    v = base_verdict(status="REVISION_PARCIAL", state_class="TERMINAL")
    assert validate_verdict_invariants(v)


def test_r1_07_suspension_con_pasa_es_violacion():
    v = base_verdict(status="PASA", state_class="OPERATIONAL_SUSPENSION")
    assert validate_verdict_invariants(v)


def test_r1_08_terminal_con_no_pasa_es_valido():
    v = base_verdict(status="NO_PASA", state_class="TERMINAL")
    assert validate_verdict_invariants(v) == []


def test_r1_09_cycle_count_no_supera_max_cycles():
    import yaml
    from jsonschema import Draft202012Validator
    schema = yaml.safe_load((BASE / "05_schema/verdict.yaml").read_text(encoding="utf-8"))
    v = base_verdict(status="NECESITA_INFO", state_class="OPERATIONAL_SUSPENSION",
                     suspension_control={"cycle_count": 3, "max_cycles": 2, "timeout_hours": 24,
                                         "target": "author", "suspension_reason": "MISSING_INFO",
                                         "missing_info_questions": ["¿?"], "unreviewed_dimensions": ["24"]})
    assert list(Draft202012Validator(schema).iter_errors(v)), "cycle_count > max_cycles debe fallar"


def test_r1_10_riesgo_no_evaluado_es_terminal_valido():
    v = base_verdict(status="RIESGO_NO_EVALUADO", state_class="TERMINAL", reason_code="TIMEBOX_EXPIRED")
    assert validate_verdict_invariants(v) == []

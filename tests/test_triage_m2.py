"""M2: split como NECESITA_INFO — recomendación de split y suspensión (4 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_triage, base_verdict  # noqa: E402
from evals.validators import validate_triage_invariants, validate_verdict_invariants  # noqa: E402


def test_01_split_con_accion_valida_es_aceptado():
    t = base_triage(triage_split_recommendation={
        "detected_macro_profiles": ["tech", "business"],
        "recommended_action": "split_artifact",
        "suspension_reason": "SPLIT_OR_SCOPE_ACCEPTANCE_REQUIRED",
    })
    assert validate_triage_invariants(t) == []


def test_02_accion_de_split_invalida_es_violacion():
    t = base_triage(triage_split_recommendation={
        "detected_macro_profiles": ["tech"],
        "recommended_action": "dividir_como_sea",
        "suspension_reason": "SPLIT_OR_SCOPE_ACCEPTANCE_REQUIRED",
    })
    errors = validate_triage_invariants(t)
    assert errors


def test_03_split_exige_veredicto_de_suspension_necesita_info():
    v = base_verdict(status="PASA", state_class="OPERATIONAL_SUSPENSION")
    errors = validate_verdict_invariants(v)
    assert errors, "OPERATIONAL_SUSPENSION con PASA debe violar la máquina de estados"


def test_04_necesita_info_con_suspension_es_valido():
    v = base_verdict(status="NECESITA_INFO", state_class="OPERATIONAL_SUSPENSION",
                     reason_code="STACK_NOT_MAPPED",
                     suspension_control={"cycle_count": 0, "max_cycles": 2, "timeout_hours": 24,
                                         "target": "author",
                                         "suspension_reason": "SPLIT_OR_SCOPE_ACCEPTANCE_REQUIRED",
                                         "missing_info_questions": ["¿dividir?"],
                                         "unreviewed_dimensions": ["24"]})
    assert validate_verdict_invariants(v) == []

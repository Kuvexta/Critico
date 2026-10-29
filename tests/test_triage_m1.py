"""M1: cap justificado — union_raw_count sobre el tope exige triage_overrides (5 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_triage  # noqa: E402
from evals.validators import validate_triage_invariants  # noqa: E402


def test_01_sobre_tope_sin_overrides_es_invalido():
    t = base_triage(dimensions_summary={"total_rubric": 108, "union_raw_count": 50,
                                        "max_active_dimensions": 40, "activated_count": 40, "pruned_count": 10},
                    active_dimensions=[str(i) for i in range(1, 41)])
    errors = validate_triage_invariants(t)
    assert any("overrides" in e.lower() or "cap" in e.lower() for e in errors), errors


def test_02_sobre_tope_con_overrides_justificados_es_valido():
    t = base_triage(dimensions_summary={"total_rubric": 108, "union_raw_count": 50,
                                        "max_active_dimensions": 40, "activated_count": 40, "pruned_count": 10},
                    active_dimensions=[str(i) for i in range(1, 41)],
                    triage_overrides=[{"dimension": "41", "reason": "dimensión crítica para el encargo"}])
    assert validate_triage_invariants(t) == []


def test_03_dentro_del_tope_sin_overrides_es_valido():
    t = base_triage(dimensions_summary={"total_rubric": 108, "union_raw_count": 3,
                                        "max_active_dimensions": 40, "activated_count": 2, "pruned_count": 1})
    assert validate_triage_invariants(t) == []


def test_04_override_sin_reason_rompe_el_schema():
    from jsonschema import Draft202012Validator
    import yaml
    schema = yaml.safe_load((BASE / "05_schema/triage.yaml").read_text(encoding="utf-8"))
    t = base_triage(triage_overrides=[{"dimension": "41"}])
    errors = list(Draft202012Validator(schema).iter_errors(t))
    assert errors, "override sin reason debería fallar el schema"


def test_05_union_es_activadas_mas_podadas():
    t = base_triage(dimensions_summary={"total_rubric": 108, "union_raw_count": 5,
                                        "max_active_dimensions": 40, "activated_count": 2, "pruned_count": 1})
    errors = validate_triage_invariants(t)
    assert errors, "activated + pruned != union debería ser violación"

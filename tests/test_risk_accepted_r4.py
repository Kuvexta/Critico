"""R4: metric_source + fallback — sin fingir evaluación cuantitativa (5 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))

from conftest import base_risk_accepted  # noqa: E402
from evals.risk_rules import validate_risk_accepted_invariants  # noqa: E402


def test_01_unavailable_con_flag_es_valido():
    r = base_risk_accepted(flag="QUANTITATIVE_UNAVAILABLE",
                           context_condition={"qualitative_trigger": "solo cualitativo"})
    assert validate_risk_accepted_invariants(r) == []


def test_02_unavailable_sin_flag_es_violacion():
    r = base_risk_accepted(context_condition={"qualitative_trigger": "solo cualitativo",
                                              "quantitative_threshold": {
                                                  "metric": "views", "comparison": "> 10",
                                                  "metric_source": "unavailable",
                                                  "evaluation_frequency": "daily",
                                                  "fallback_to_qualitative": True}})
    assert validate_risk_accepted_invariants(r)


def test_03_fuente_real_sin_flag_es_valido():
    r = base_risk_accepted(context_condition={"qualitative_trigger": "umbral",
                                              "quantitative_threshold": {
                                                  "metric": "views", "comparison": "> 10",
                                                  "metric_source": "dashboard",
                                                  "evaluation_frequency": "daily",
                                                  "fallback_to_qualitative": True}})
    assert validate_risk_accepted_invariants(r) == []


def test_04_quantitative_threshold_exige_metric_source():
    import yaml
    from jsonschema import Draft202012Validator
    schema = yaml.safe_load((BASE / "05_schema/risk_accepted.yaml").read_text(encoding="utf-8"))
    r = base_risk_accepted(context_condition={"qualitative_trigger": "umbral",
                                              "quantitative_threshold": {
                                                  "metric": "views", "comparison": "> 10",
                                                  "evaluation_frequency": "daily"}})
    assert list(Draft202012Validator(schema).iter_errors(r))


def test_05_expiration_date_obligatoria():
    import yaml
    from jsonschema import Draft202012Validator
    schema = yaml.safe_load((BASE / "05_schema/risk_accepted.yaml").read_text(encoding="utf-8"))
    r = {k: v for k, v in base_risk_accepted().items() if k != "expiration_date"}
    assert list(Draft202012Validator(schema).iter_errors(r))

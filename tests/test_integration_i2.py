"""I2: relación padre-hijo entre pasos de un plan (5 tests)."""
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


def test_01_objection_acepta_parent_id():
    o = base_objection(parent_id="ART-PADRE", step_index=2)
    assert not list(Draft202012Validator(OBJ).iter_errors(o))


def test_02_step_index_exige_entero_positivo():
    o = base_objection(parent_id="ART-PADRE", step_index=0)
    assert list(Draft202012Validator(OBJ).iter_errors(o))


def test_03_triage_acepta_parent_id_y_source_stack():
    t = base_triage(parent_id="ART-PADRE", source_stack="stack_1")
    assert not list(Draft202012Validator(TRI).iter_errors(t))


def test_04_plan_status_con_los_siete_campos():
    t = base_triage(plan_status={"parent_id": "ART-PADRE", "total_steps": 7,
                                 "steps_passed": 3, "steps_blocked": 1,
                                 "steps_pending": 3, "blocked_at_step": 4,
                                 "plan_verdict": "blocked"})
    assert not list(Draft202012Validator(TRI).iter_errors(t))


def test_05_plan_cascade_bloquea_pasos_aguas_abajo():
    cascade = (CONFIG.get("integration") or {}).get("plan_cascade") or {}
    assert cascade.get("on_step_blocked", {}).get("action") == "block_downstream_steps"

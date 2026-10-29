"""I1: mapeo stack BZ-109 → macro-perfil (4 tests)."""
import sys
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

CONFIG = yaml.safe_load((BASE / "04_critic.config.yaml").read_text(encoding="utf-8"))
INTEG = CONFIG.get("integration") or {}


def test_01_existe_la_tabla_de_stacks():
    mapping = INTEG.get("bz109_stack_mapping") or {}
    assert mapping, "bz109_stack_mapping debe existir en critic.config.yaml"


def test_02_cada_stack_mapea_a_macro_perfil_valido():
    mapping = INTEG.get("bz109_stack_mapping") or {}
    valid = {"tech", "legal", "business", "personal", "health", "ops"}
    for stack, entry in mapping.items():
        assert entry.get("macro_profile") in valid, f"{stack} con macro_perfil inválido"


def test_03_stack_no_mapeado_pide_clarificacion():
    behavior = INTEG.get("unmapped_stack_behavior") or {}
    assert behavior.get("action") == "NECESITA_INFO"
    assert behavior.get("suspension_reason") == "STACK_NOT_MAPPED"


def test_04_stack_3_pendiente_no_bloquea():
    mapping = INTEG.get("bz109_stack_mapping") or {}
    assert mapping.get("stack_3", {}).get("status") == "pending_confirmation"

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


def test_04_stack_3_eliminado_y_stack_no_mapeado_pide_clarificacion():
    """CAMBIO INTENCIONAL DE CONTRATO — NO es un ajuste para que el test pase.

    Aprobado por Dirección (Andrés): MD-4, GATE C concedido, BZ-20261030-094,
    con las condiciones fijadas el 2026-10-30: (1) este cambio se documenta
    como intencional con su motivo y su diff exacto; (2) la suite debe quedar
    153/153 calculada; (3) commit solo local; (4) verificación de segundo
    nivel por un verificador aparte.

    MOTIVO: el Registro Canónico F/T/S/E v1 (hash d7d2d870…) resuelve la
    incógnita `stack_3` de BZ-109: no existe «stack_3» — la ambigüedad se
    disuelve en `E-3` (datos) y `T3` (conocimiento/memoria). El estado viejo
    (`stack_3.status == pending_confirmation`) queda ELIMINADO, y con él la
    aserción que lo congelaba.

    El test sigue verificando algo real del contrato I1 (§4.7 del FROZEN):
      1. el estado viejo ya no existe (`stack_3` ausente del mapping);
      2. la tabla nueva tiene exactamente las 34 entradas F/T/S/E;
      3. un stack NO mapeado con id nuevo («X-1») → NECESITA_INFO con
         suspension_reason STACK_NOT_MAPPED (el sistema no rompe: pide
         clarificación).
    """
    mapping = INTEG.get("bz109_stack_mapping") or {}
    # 1. Estado viejo eliminado (contrato nuevo aprobado por Dirección).
    assert "stack_3" not in mapping, "stack_3 debe estar eliminado (MD-4 lo disuelve en E-3 y T3)"
    # 2. Tabla nueva completa: 34 entradas del Registro Canónico F/T/S/E v1.
    esperadas = {
        *(f"E-{i}" for i in range(1, 11)),   # E-1 … E-10
        *(f"E-S{i}" for i in range(1, 6)),   # E-S1 … E-S5
        *("F1", "F4", "F5", "F6", "F7", "F8"),
        *(f"T{i}" for i in range(1, 6)),     # T1 … T5
        *(f"S{i:02d}" for i in range(1, 9)), # S01 … S08
    }
    assert len(mapping) == 34, f"se esperaban 34 entradas F/T/S/E, hay {len(mapping)}"
    assert set(mapping) == esperadas, "claves del mapping ≠ Registro Canónico F/T/S/E v1"
    # 3. Contrato I1 en acción: stack NO mapeado (id nuevo «X-1») → NECESITA_INFO + STACK_NOT_MAPPED.
    assert "X-1" not in mapping
    behavior = INTEG.get("unmapped_stack_behavior") or {}
    assert behavior.get("action") == "NECESITA_INFO"
    assert behavior.get("suspension_reason") == "STACK_NOT_MAPPED"

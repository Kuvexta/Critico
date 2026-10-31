"""Sub-perfil ops.cosecha (PROP-COSECHA-001 · v3.5.0): mapeo C01–C13 a IDs
reales de la rúbrica, composición (C02 compuesto, C07 AND), severidades
condicionales y parámetros del dominio prc. 13 tests — aditivos: no tocan
ningún contrato de la suite histórica."""
import hashlib
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
RUBRIC = yaml.safe_load((BASE / "03_rubric.yaml").read_text(encoding="utf-8"))
CONFIG = yaml.safe_load((BASE / "04_critic.config.yaml").read_text(encoding="utf-8"))


def _sub():
    return CONFIG["profiles"]["universals"]["ops"]["sub_profiles"].get("ops.cosecha")


def _slots():
    return CONFIG["cosecha_prc"]["slots"]


def test_01_ops_cosecha_existe_como_sub_perfil_de_ops():
    assert _sub() is not None, "ops.cosecha ausente en profiles.universals.ops.sub_profiles"


def test_02_suggested_dimensions_15_ids_en_orden_c01_c13():
    assert _sub()["suggested_dimensions"] == [30, 3, 32, 100, 50, 9, 88, 57, 44, 55, 41, 23, 79, 17, 106]


def test_03_suggested_dimensions_dentro_del_catalogo_1_108():
    ids = {d["id"] for d in RUBRIC["dimensions"]}
    assert set(_sub()["suggested_dimensions"]) <= ids


def test_04_mapeo_c01_c13_a_ids_reales_de_la_rubrica():
    esperado = {
        "C01": [30], "C02": [3], "C03": [32], "C04": [100], "C05": [50], "C06": [9],
        "C07": [88, 57], "C08": [44], "C09": [55], "C10": [41], "C11": [23],
        "C12": [79], "C13": [17, 106],
    }
    for slot, dims in esperado.items():
        assert _slots()[slot]["dimensions"] == dims, f"{slot}: {_slots()[slot]['dimensions']}"


def test_05_c07_es_and_con_reporte_separado():
    c07 = _slots()["C07"]
    assert c07["severity"] == "bloqueante"
    assert "AND" in c07["composicion"]
    assert "separado" in c07["composicion"]


def test_06_c02_es_compuesto_no_alias_con_delta_y_replay():
    c02 = _slots()["C02"]
    assert "compuesto" in c02["composicion"]
    assert "alias" in c02["composicion"]  # declara explícitamente que NO es alias
    assert "δ" in c02["composicion"]
    assert "replay" in c02["composicion"]


def test_07_c11_severidad_condicional_por_tipo():
    c11 = _slots()["C11"]
    assert c11["severity"] == "condicional"
    assert "SKILL" in c11["regla"]
    assert "PROMPT_CANONICO" in c11["regla"]
    assert "DEGRADAR" in c11["regla"]


def test_08_c12_c13_advisory_con_escalado_beta_wilson_y_baseline_version():
    for slot in ("C12", "C13"):
        s = _slots()[slot]
        assert s["severity"] == "advisory"
        assert "Beta/Wilson" in s["escalado"]
        assert "baseline_version" in s["escalado"]


def test_09_parametros_dominio_prc_estrictos():
    prc = CONFIG["cosecha_prc"]
    assert prc["domain"] == "prc"
    assert prc["sub_profile_id"] == "ops.cosecha"
    assert prc["pointer_enforcement_strict"] is True
    assert prc["snapshot_hash_validation"] is True


def test_10_p29_matriz_binaria_con_bypass():
    p29 = CONFIG["cosecha_prc"]["p29_matrix"]
    assert p29["binary"] is True
    assert set(p29["obliga_ficha_si"]) == {"recurrente", "multi_agente", "toca_canonicos"}
    assert "BYPASS" in p29["bypass_si"]


def test_11_guia_documenta_el_bundle_completo():
    guia = (BASE / "docs" / "guia_subperfil_ops_cosecha.md").read_text(encoding="utf-8")
    for token in ("ops.cosecha", "C02", "C07", "C13", "AND", "BYPASS", "pointer_enforcement_strict",
                  "snapshot_hash_validation", "88", "57", "Beta/Wilson"):
        assert token in guia, f"la guía no documenta: {token}"


def test_12_u2_intacto_6_macro_perfiles_sin_cambio():
    assert set(CONFIG["profiles"]["universals"].keys()) == {"tech", "business", "ops", "legal", "health", "personal"}


def test_13_config_hash_recalculado_con_convencion_de_contributing():
    raw = (BASE / "04_critic.config.yaml").read_text(encoding="utf-8")
    lineas = [l for l in raw.splitlines(keepends=True) if not l.lstrip().startswith("config_hash:")]
    esperado = hashlib.sha256("".join(lineas).encode("utf-8")).hexdigest()
    assert CONFIG["config_hash"] == esperado

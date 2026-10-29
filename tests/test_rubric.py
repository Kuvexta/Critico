"""Rubric: 108 ids únicos, 19 familias, leyendas y freeze (8 tests)."""
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RUBRIC = yaml.safe_load((BASE / "03_rubric.yaml").read_text(encoding="utf-8"))


def _dims():
    return RUBRIC.get("dimensions") or []


def _ids():
    return [str(d.get("id")) for d in _dims()]


def test_01_total_dimensions_108():
    assert RUBRIC.get("total_dimensions") == 108
    assert len(_dims()) == 108


def test_02_ids_unicos_sin_duplicados():
    ids = _ids()
    assert len(ids) == len(set(ids))


def test_03_ids_contiguos_1_a_108():
    nums = sorted(int(i) for i in _ids())
    assert nums == list(range(1, 109))


def test_04_19_familias_declaradas():
    fams = RUBRIC.get("families") or []
    assert len(fams) == 19


def test_05_familias_declaradas_de_A_a_S():
    fams = RUBRIC.get("families") or []
    assert fams == [chr(c) for c in range(ord("A"), ord("S") + 1)]


def test_06_cada_dimension_con_key_unica_y_activacion_valida():
    seen = set()
    for d in _dims():
        key = d.get("key")
        assert key and isinstance(key, str) and not key.startswith("<"), f"dimensión {d.get('id')} sin key"
        assert key not in seen, f"key duplicada: {key}"
        seen.add(key)
        assert d.get("act") in ("core", "dom", "opt"), f"dimensión {d.get('id')} con act inválida {d.get('act')}"


def test_07_leyendas_activation_y_v1_angle():
    assert "activation_legend" in RUBRIC
    assert "v1_angle_legend" in RUBRIC


def test_08_frozen_declarado():
    assert RUBRIC.get("frozen") is True

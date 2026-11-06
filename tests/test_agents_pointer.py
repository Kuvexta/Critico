"""CRITICO-SKILL-02 · AGENTS.md es un puntero al canon, sin copiar políticas.

Si CANON_PATH apunta a una copia del canon (p. ej. el espejo privado), se
verifican VERSION y los sha256; si no, se comprueba solo la forma (CI público)."""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).resolve().parents[1]
TEXT = (BASE / "AGENTS.md").read_text(encoding="utf-8")


def _pointer() -> dict:
    m = re.search(r"## Gobernanza: puntero al canon.*?```yaml\n(.*?)```", TEXT, re.S)
    assert m, "falta el bloque puntero en AGENTS.md"
    return yaml.safe_load(m.group(1))


def test_01_campos_del_puntero():
    p = _pointer()
    assert set(p) == {"canon_path", "canon_version", "canon_sha256", "precedence", "stale_if_mismatch"}
    assert p["canon_version"] == "2026.11.05.1"
    assert p["stale_if_mismatch"] is True
    assert set(p["canon_sha256"]) == {"VERSION", "SHA256SUMS"}
    assert all(re.fullmatch(r"[0-9a-f]{64}", v) for v in p["canon_sha256"].values())


def test_02_sin_kit_viejo_copiado():
    assert "KIT OBLIGATORIO" not in TEXT
    assert not re.search(r"P01[–-]P2[0-9]\b", TEXT), "no se copian rangos de políticas viejos"


@pytest.mark.skipif(not os.environ.get("CANON_PATH"), reason="CANON_PATH no definido (canon privado)")
def test_03_hashes_coinciden_con_el_canon():
    canon = Path(os.environ["CANON_PATH"])
    p = _pointer()
    for name, expected in p["canon_sha256"].items():
        assert hashlib.sha256((canon / name).read_bytes()).hexdigest() == expected, name
    assert f"VERSION={p['canon_version']}" in (canon / "VERSION").read_text(encoding="utf-8")

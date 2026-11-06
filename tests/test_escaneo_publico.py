"""CRITICO-SKILL-02 · escaneo público: 0 hallazgos nuevos frente a la línea base
y detección de hallazgos sintéticos (sin datos reales)."""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
import escaneo_publico as esc  # noqa: E402


def test_01_sin_hallazgos_nuevos_en_el_arbol():
    assert esc.new_findings(esc.scan(), esc.load_baseline()) == []


def test_02_golden_set_incluido_en_el_escaneo():
    assert any(n.startswith("09_golden_set/") for n in esc.tracked_files())


def test_03_detecta_sinteticos(tmp_path, monkeypatch):
    f = tmp_path / "x.md"
    f.write_text("contacto: persona@ejemplo.invalid · NIT 900.123.456-7 · ref BZ-20990101-001\n", encoding="utf-8")
    monkeypatch.setattr(esc, "BASE", tmp_path)
    reglas = {r for (_, r, _) in esc.new_findings(esc.scan(["x.md"]), esc.Counter())}
    assert {"email", "nit_cedula_co", "id_interno_bz"} <= reglas


def test_04_nombres_extra_por_entorno(tmp_path, monkeypatch):
    (tmp_path / "y.md").write_text("Lo firmó Zacarías.\n", encoding="utf-8")
    monkeypatch.setattr(esc, "BASE", tmp_path)
    monkeypatch.setenv("ESCANEO_NOMBRES", "Zacarías")
    assert any(r == "nombre_real_extra" for (_, r, _) in esc.scan(["y.md"]))


def test_05_versiones_no_son_nit():
    assert not esc.rules()["nit_cedula_co"].search("v3.6.0 · 01.00.01 · 2026-11-06")

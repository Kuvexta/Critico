"""CRITICO-SKILL-02 · PR-B punto 10: referencia de integraciones (C1–C7)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
import package_cli_ide_skills as gen  # noqa: E402

REF = BASE / "skills" / "critico" / "references"
DOCS = (REF / "integraciones.md", REF / "en" / "integrations.md")
# Marcas reales que NO deben aparecer (proveedores solo como ejemplo neutro).
MARCAS = r"stripe|paypal|mercado ?(libre|pago)|amazon|shopify|dhl|fedex|ups\b|servientrega|wompi|payu|adyen|ebay"


def test_01_c1_a_c7_en_ambos_idiomas():
    for doc in DOCS:
        texto = doc.read_text(encoding="utf-8")
        assert [f"C{n}" for n in range(1, 8)] == sorted(set(re.findall(r"\*\*(C[1-7])\*\*", texto)))


def test_02_carga_condicional_desde_la_skill():
    es = (BASE / "skills/critico/SKILL.es.md").read_text(encoding="utf-8")
    en = (BASE / "skills/critico/SKILL.md").read_text(encoding="utf-8")
    assert "references/integraciones.md" in es and "solo si el artefacto toca pagos, marketplace, envíos o APIs externas" in es
    assert "references/en/integrations.md" in en and "only when the artifact touches payments, marketplaces, shipping or external APIs" in en


def test_03_sin_marcas_reales_ni_ids_internos():
    for doc in DOCS:
        texto = doc.read_text(encoding="utf-8")
        assert not re.search(MARCAS, texto, re.I), doc
        assert not re.search(r"\b(BZ|ENC|MD|PRC)-\d", texto), doc


def test_04_viaja_en_las_13_variantes():
    assert "references/integraciones.md" in gen.REFERENCES and "references/en/integrations.md" in gen.REFERENCES
    for v in gen.variants():
        for ref in ("integraciones.md", "en/integrations.md"):
            assert (gen.REPO_OUT / v["id"] / "critico/references" / ref).is_file(), (v["id"], ref)

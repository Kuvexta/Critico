"""CRITICO-SKILL-02 · la skill no diverge del prompt v3.6 ni de critico_cli.ANGLES.

Fuente única del Pre-Report Gate: paso 4-bis de prompts/critico_system.md (ES) y
prompts/critic_system.en.md (EN). Fuente única de los ángulos: critico_cli.ANGLES
(títulos ES) y locales/en.json (títulos EN)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "scripts"))
import critico_cli  # noqa: E402
import package_cli_ide_skills as gen  # noqa: E402

REF = BASE / "skills" / "critico" / "references"
PARES = (("metodo.md", "prompts/critico_system.md", "es"), ("en/method.md", "prompts/critic_system.en.md", "en"))


def _titulos(lang: str) -> list[str]:
    if lang == "es":
        return [t for _, t, _ in critico_cli.ANGLES]
    loc = json.loads((BASE / "locales" / "en.json").read_text(encoding="utf-8"))
    return [loc[f"angle.{n}.title"] for n, _, _ in critico_cli.ANGLES]


def _norm(s: str) -> str:
    s = re.sub(r"\((⭐|opcional|optional|v3\.6)\)", "", s.lower())
    return re.sub(r"[\s\-]+", " ", s.replace("⭐", "")).strip()


def _bloque(texto: str, inicio: str, fin: str) -> str:
    i, j = texto.index(inicio), texto.index(fin)
    return texto[texto.index("\n", i) + 1:j]


def test_01_quince_angulos_en_la_fuente():
    assert [n for n, _, _ in critico_cli.ANGLES] == list(range(1, 16))


def test_02_skill_lista_los_15_angulos_exactos():
    for ref, _, lang in PARES:
        texto = (REF / ref).read_text(encoding="utf-8")
        lineas = [l for l in _bloque(texto, "<!-- ANGULOS:BEGIN", "<!-- ANGULOS:END -->").splitlines() if l.strip()]
        assert lineas == [f"{n}. {t}" for n, t in zip(range(1, 16), _titulos(lang))], ref


def test_03_prompts_nombran_los_15_angulos():
    for _, prompt, lang in PARES:
        paso3 = next(l for l in (BASE / prompt).read_text(encoding="utf-8").splitlines() if l.startswith("3. "))
        for n, titulo in zip(range(1, 16), _titulos(lang)):
            m = re.search(r"\(%d\) ([^·—(]+)" % n, paso3)
            assert m, (prompt, n)
            assert _norm(titulo) in _norm(m.group(1)) or _norm(m.group(1)) in _norm(titulo), (prompt, n, titulo, m.group(1))


def test_04_pre_report_gate_identico_al_prompt():
    for ref, prompt, _ in PARES:
        texto = (REF / ref).read_text(encoding="utf-8")
        bloque = _bloque(texto, gen.GATE_BEGIN, gen.GATE_END).strip("\n")
        assert bloque == gen.gate_step(prompt), ref
        assert texto.count("4-bis.") == 1, "el paso 4-bis no se duplica fuera del bloque generado: " + ref


def test_05_generador_detecta_divergencia(tmp_path, monkeypatch):
    reference, prompt = gen.GATE_SYNC[0]
    destino = tmp_path / reference
    destino.parent.mkdir(parents=True)
    texto = (gen.SOURCE / reference).read_text(encoding="utf-8").replace("(a) ¿puedo citar", "(a) ¿podría citar")
    destino.write_text(texto, encoding="utf-8")
    monkeypatch.setattr(gen, "SOURCE", tmp_path)
    assert destino.read_bytes() != gen.synced_reference(reference, prompt)

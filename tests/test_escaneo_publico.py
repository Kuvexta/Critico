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
    # Construidos por concatenación para que este archivo no contenga el literal detectable.
    sintetico = "contacto: persona" + "@" + "ejemplo.invalid · NIT 900.123" + ".456-7 · ref BZ-" + "20990101-001\n"
    f.write_text(sintetico, encoding="utf-8")
    monkeypatch.setattr(esc, "BASE", tmp_path)
    reglas = {r for (_, r, _) in esc.new_findings(esc.scan(["x.md"]), esc.Counter())}
    assert {"email", "nit_cedula_co", "id_interno_bz"} <= reglas


def test_04_nombres_extra_por_entorno(tmp_path, monkeypatch):
    (tmp_path / "y.md").write_text("Lo firmó Zacarías.\n", encoding="utf-8")
    monkeypatch.setattr(esc, "BASE", tmp_path)
    monkeypatch.setenv("ESCANEO_NOMBRES", "Zacarías")
    assert any(r == "nombre_real" for (_, r, _) in esc.scan(["y.md"]))


def test_07_sin_nombres_fijos_en_el_codigo(monkeypatch):
    monkeypatch.delenv("ESCANEO_NOMBRES", raising=False)
    assert "nombre_real" not in esc.rules()
    assert "nombre_real" not in esc.RULES


def test_05_versiones_no_son_nit():
    assert not esc.rules()["nit_cedula_co"].search("v3.6.0 · 01.00.01 · 2026-11-06")


def test_06_no_escaneables_se_informan(tmp_path, monkeypatch):
    (tmp_path / "b.bin").write_bytes(b"\xff\xfe\x00binario")
    monkeypatch.setattr(esc, "BASE", tmp_path)
    esc.scan(["b.bin"])
    assert esc.SKIPPED == ["b.bin"]


# --- Secreto ESCANEO_NOMBRES en CI (decisión de Dirección en #3) ---------------------------

NOMBRE_SINTETICO = "Zacarías Quintanilla"          # ficticio; solo se busca vía ESCANEO_NOMBRES
CORREO_SINTETICO = "persona" + "@" + "ejemplo.invalid"  # concatenado: este archivo no lo contiene literal


def _repo_temporal(tmp_path, contenido: str) -> Path:
    import shutil
    import subprocess as sp
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir()
    shutil.copy(BASE / "scripts" / "escaneo_publico.py", repo / "scripts" / "escaneo_publico.py")
    (repo / "x.md").write_text(contenido, encoding="utf-8")
    sp.run(["git", "init", "-q"], cwd=repo, check=True)
    sp.run(["git", "add", "-A"], cwd=repo, check=True)
    return repo


def _correr(repo: Path, nombres: str | None, *args: str, ci: bool = False):
    import os
    import subprocess as sp
    env = {k: v for k, v in os.environ.items() if k not in ("ESCANEO_NOMBRES", "CI", "GITHUB_ACTIONS")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if ci:
        env["CI"] = env["GITHUB_ACTIONS"] = "true"
    if nombres is not None:
        env["ESCANEO_NOMBRES"] = nombres
    r = sp.run([sys.executable, "-B", "scripts/escaneo_publico.py", *args], cwd=repo, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def test_08_modo_ci_nombre_real_solo_cuenta_sin_ruta_linea_ni_termino(tmp_path):
    repo = _repo_temporal(tmp_path, f"uno\ndos\nfirma: {NOMBRE_SINTETICO}\ncuatro\ncontacto {CORREO_SINTETICO}\n")
    rc, salida = _correr(repo, NOMBRE_SINTETICO, ci=True)
    assert rc == 1
    assert "regla nombre_real: 1 coincidencia(s) nueva(s)" in salida
    assert "x.md:3" not in salida and "x.md" not in [l for l in salida.splitlines() if "nombre_real" in l][0]
    assert not any("nombre_real" in l and ":3" in l for l in salida.splitlines())
    assert "x.md:5: regla email" in salida            # las demás reglas siguen con ruta y línea
    for secreto in (NOMBRE_SINTETICO, "Zacarías", "Quintanilla", CORREO_SINTETICO, "ejemplo.invalid"):
        assert secreto not in salida, secreto


def test_08b_detalle_local_muestra_ruta_y_linea_pero_no_el_termino(tmp_path):
    repo = _repo_temporal(tmp_path, f"uno\ndos\nfirma: {NOMBRE_SINTETICO}\n")
    rc, salida = _correr(repo, NOMBRE_SINTETICO, "--detalle")
    assert rc == 1 and "x.md:3: regla nombre_real" in salida
    assert NOMBRE_SINTETICO not in salida and "Zacarías" not in salida


def test_08c_detalle_rechazado_en_ci_o_sin_secreto(tmp_path):
    repo = _repo_temporal(tmp_path, f"firma: {NOMBRE_SINTETICO}\n")
    rc, salida = _correr(repo, NOMBRE_SINTETICO, "--detalle", ci=True)
    assert rc == 2 and "no se permite en CI" in salida and "x.md" not in salida
    rc, salida = _correr(repo, None, "--detalle")
    assert rc == 2 and "requiere ESCANEO_NOMBRES" in salida


def test_09_sin_secreto_o_vacio_avisa_y_no_falla(tmp_path):
    repo = _repo_temporal(tmp_path, f"firma: {NOMBRE_SINTETICO}\n")
    for valor in (None, "", "   "):          # sin variable (fork) o secreto vacío
        rc, salida = _correr(repo, valor)
        assert rc == 0, salida
        assert "ESCANEO_AVISO: ESCANEO_NOMBRES no definido o vacío" in salida
        assert NOMBRE_SINTETICO not in salida


def test_10_ci_pasa_el_secreto_al_paso_de_escaneo():
    import yaml
    wf = yaml.safe_load((BASE / ".github/workflows/critico-ci.yml").read_text(encoding="utf-8"))
    pasos = [s for job in wf["jobs"].values() for s in job["steps"]]
    paso = next(s for s in pasos if "escaneo_publico.py" in s.get("run", ""))
    assert paso["env"]["ESCANEO_NOMBRES"] == "${{ secrets.ESCANEO_NOMBRES }}"

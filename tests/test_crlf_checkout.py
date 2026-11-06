"""CRITICO-SKILL-02 · PR-B: un checkout con core.autocrlf=true (el de Windows por
defecto) debe dar el MISMO resultado en verificar_release y verify_freeze.

Clona HEAD (estado confirmado, como en CI) con autocrlf=true y compara rc y
salida con los del árbol de trabajo. Sin `.gitattributes` (eol=lf), el clon
recibe CRLF y verificar_release falla por hash distinto (hallazgo de la
revisión cruzada en Windows)."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
SCRIPTS = ("scripts/verificar_release.py", "scripts/verify_freeze.py")
CRLF_A_PROPOSITO = "licencias/DECISION_PENDIENTE.json"


def _run(cwd: Path, script: str) -> tuple[int, str]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", script], cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


@pytest.fixture(scope="module")
def clon_crlf(tmp_path_factory):
    if shutil.which("git") is None or subprocess.run(["git", "rev-parse", "HEAD"], cwd=BASE,
                                                       capture_output=True).returncode != 0:
        pytest.fail("se requiere git con HEAD para simular el checkout CRLF (no se omite en silencio)")
    destino = tmp_path_factory.mktemp("crlf") / "repo"
    subprocess.run(["git", "-c", "core.autocrlf=true", "clone", "-q", "--no-hardlinks", str(BASE), str(destino)],
                   check=True, capture_output=True)
    subprocess.run(["git", "config", "core.autocrlf", "true"], cwd=destino, check=True)
    return destino


def test_01_checkout_crlf_mantiene_lf_en_archivos_con_hash(clon_crlf):
    for rel in ("04_critic.config.yaml", "CHANGELOG.md", "docs/HASHES.md", "MANIFEST.json",
                "skills/critico/references/metodo.md", "plataformas/codex/critico/SKILL.md"):
        assert b"\r\n" not in (clon_crlf / rel).read_bytes(), rel


def test_02_crlf_a_proposito_se_conserva_byte_a_byte(clon_crlf):
    original = subprocess.run(["git", "show", f"HEAD:{CRLF_A_PROPOSITO}"], cwd=BASE, capture_output=True,
                              check=True).stdout
    assert b"\r\n" in original
    assert (clon_crlf / CRLF_A_PROPOSITO).read_bytes() == original


@pytest.mark.parametrize("script", SCRIPTS)
def test_03_mismo_resultado_con_y_sin_crlf(clon_crlf, script):
    rc_lf, out_lf = _run(BASE, script)
    rc_crlf, out_crlf = _run(clon_crlf, script)
    assert (rc_crlf, out_crlf) == (rc_lf, out_lf)
    assert rc_crlf == 0, out_crlf

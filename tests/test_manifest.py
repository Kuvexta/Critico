"""CRITICO-SKILL-02 · MANIFEST.json reproducible (punto 3)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
import build_manifest as bm  # noqa: E402


def test_01_manifest_reproducible_igual():
    assert bm.build() == bm.build()
    assert bm.MANIFEST.read_bytes() == bm.build(), "MANIFEST.json desactualizado: scripts/build_manifest.py --write"


def test_02_lista_ordenada_y_hash_agregado_estilo_sha256sum():
    m = json.loads(bm.MANIFEST.read_text(encoding="utf-8"))
    paths = [e["path"] for e in m["files"]]
    assert paths == sorted(paths, key=lambda s: s.encode("utf-8"))
    lineas = "".join(f"{e['sha256']}  {e['path']}\n" for e in m["files"])
    assert m["aggregate_sha256"] == hashlib.sha256(lineas.encode("utf-8")).hexdigest()
    for e in m["files"]:
        assert hashlib.sha256((BASE / e["path"]).read_bytes()).hexdigest() == e["sha256"], e["path"]


def test_03_alcance_incluye_y_excluye():
    paths = {e["path"] for e in json.loads(bm.MANIFEST.read_text(encoding="utf-8"))["files"]}
    for obligatorio in ("04_critic.config.yaml", "prompts/critico_system.md", "prompts/critic_system.en.md",
                        "skills/critico/SKILL.md", "plataformas/codex/critico/agents/openai.yaml"):
        assert obligatorio in paths
    assert len({p.split("/")[1] for p in paths if p.startswith("plataformas/")}) == 13
    assert not any(p.startswith(("plataformas/codex/README", "plataformas/codex/LICENSE")) for p in paths)
    assert not any(x in p for p in paths for x in (".git/", "_tmp_pruebas", "__pycache__", ".pyc"))


def test_04_check_detecta_cambio(tmp_path, monkeypatch):
    alterado = tmp_path / "MANIFEST.json"
    alterado.write_bytes(bm.build().replace(b'"count"', b'"count_"'))
    monkeypatch.setattr(bm, "MANIFEST", alterado)
    monkeypatch.setattr(sys, "argv", ["build_manifest.py", "--check"])
    assert bm.main() == 1


def test_05_cli_check_sin_escrituras():
    antes = bm.MANIFEST.read_bytes()
    r = subprocess.run([sys.executable, "-B", str(BASE / "scripts/build_manifest.py"), "--check"],
                       capture_output=True, text=True, cwd=BASE)
    assert r.returncode == 0, r.stderr
    assert bm.MANIFEST.read_bytes() == antes

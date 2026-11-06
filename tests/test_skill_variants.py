"""CRITICO-SKILL-02 · variantes de la skill: el generador existente reproduce
plataformas/ byte a byte, --check es idempotente y detecta deriva."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
import package_cli_ide_skills as gen  # noqa: E402

PLATAFORMAS_ESPERADAS = {
    "antigravity", "claude-code", "cline", "codex", "cursor", "deepseek-harness", "gemini-cli",
    "github-copilot", "kiro", "openclaw", "opencode", "qwen-code", "universal",
}


def _tree_digest() -> str:
    h = hashlib.sha256()
    for p in sorted(gen.REPO_OUT.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(BASE).as_posix().encode() + b"\0" + p.read_bytes())
    h.update(gen.REPO_MANIFEST.read_bytes())
    return h.hexdigest()


def test_01_trece_variantes():
    assert {v["id"] for v in gen.variants()} == PLATAFORMAS_ESPERADAS
    assert {p.name for p in gen.REPO_OUT.iterdir() if p.is_dir()} == PLATAFORMAS_ESPERADAS


def test_02_byte_a_byte():
    files = gen.candidate_files()
    disk = gen.repo_disk()
    assert set(files) == set(disk)
    distintos = [n for n in files if files[n] != disk[n]]
    assert distintos == []


def test_03_manifest_al_dia():
    files = gen.candidate_files()
    assert gen.REPO_MANIFEST.read_bytes() == gen.repo_manifest(files)
    assert gen.repo_problems(files, gen.repo_manifest(files)) == []


def test_04_check_idempotente_y_sin_escrituras():
    antes = _tree_digest()
    for _ in range(2):
        r = subprocess.run([sys.executable, "-B", str(BASE / "scripts/package_cli_ide_skills.py"), "--check"],
                           capture_output=True, text=True, cwd=BASE)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "CHECK_OK" in r.stdout
    assert _tree_digest() == antes


def test_05_check_detecta_deriva():
    files = gen.candidate_files()
    victima = sorted(files)[0]
    alterado = dict(files)
    alterado[victima] = files[victima] + b"x"
    problemas = gen.repo_problems(alterado, gen.repo_manifest(alterado))
    assert any(victima in p for p in problemas)


def test_06_disable_model_invocation_se_conserva():
    for v in gen.variants():
        data = (gen.REPO_OUT / v["id"] / "critico/SKILL.md").read_bytes()
        meta, _ = gen.frontmatter(data)
        if v["control"] == "flag":
            assert meta.get("disable-model-invocation") is True, v["id"]
        else:
            assert "disable-model-invocation" not in meta, v["id"]


def test_07_hash_legado_como_referencia():
    import json
    m = json.loads(gen.REPO_MANIFEST.read_text(encoding="utf-8"))
    assert m["legacy_proposal_sha256"] == "01a38240c71a825318a2fff0761e0def132528976f973677f1896cfd4b23a6e2"
    assert m["variants"] == 13

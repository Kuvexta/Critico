"""CRITICO-SKILL-02 · punto 11: golden set de contrato de la skill.
«Falla con la vieja y pasa con la nueva» como comando reproducible."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from evals import skill_contract as sc  # noqa: E402

OBJETIVO = {"SC-001", "SC-002", "SC-003"}


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-m", "evals.cli", *args], cwd=BASE, capture_output=True, text=True)


def test_01_nueva_pasa_todo():
    out = sc.run("new")
    assert out["passed"] == out["total"] == 4, out
    assert out["rules"] == ["R_BINDING", "R_INTEG", "R_MODE"]


def test_02_vieja_falla_los_tres_casos_objetivo_y_pasa_el_control():
    out = sc.run("old")
    assert out["rules"] == []
    fallidos = {c["case_id"] for c in out["cases"] if not c["passed"]}
    assert fallidos == OBJETIVO


def test_03_comando_reproducible():
    assert _cli("--skill-version", "old", "--expect-all-pass", "--json").returncode == 1
    assert _cli("--skill-version", "new", "--expect-all-pass", "--json").returncode == 0
    assert _cli("--skill-version", "new", "--fail-on-regression", "--json").returncode == 0


def test_04_baseline_y_ratchet(tmp_path):
    base = sc.load_baseline()
    assert base["new"]["passed"] == 4 and base["old"]["passed"] == 1
    destino = tmp_path / "b.json"
    sc.write_baseline({"skill_version": "new", "passed": 4, "total": 4, "rules": []}, destino)
    with pytest.raises(ValueError, match="ratchet"):
        sc.write_baseline({"skill_version": "new", "passed": 3, "total": 4, "rules": []}, destino)
    assert sc.regression({"skill_version": "new", "passed": 3}, sc.load_baseline(destino))


def test_05_independencia_ausente_no_se_presume():
    caso = {"review": {"mode": "INDEPENDIENTE", "claims_gate_b": True, "status": "PASA",
                       "artifact_binding": {"head": "h", "bundle_sha256": "b"}},
            "artifact_current": {"head": "h", "bundle_sha256": "b"}}
    r = sc.evaluate(caso, {"R_MODE"})
    assert r["mode"] == "AUTOCONTROL" and r["codes"] == ["AUTOCONTROL_COMO_GATE_B"]


def test_06_version_vieja_inaccesible_no_es_silenciosa(monkeypatch):
    monkeypatch.setattr(sc, "OLD_SKILL_REF", "0" * 40)
    with pytest.raises(sc.SkillSourceError):
        sc.run("old")


def test_07_casos_sinteticos_con_bloque_expected():
    for caso in sc.load_cases():
        assert caso["metadata"]["synthetic"] is True
        assert set(caso["expected"]) == {"mode", "status", "blockers", "codes", "artifact_binding"}

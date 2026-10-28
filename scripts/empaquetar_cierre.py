#!/usr/bin/env python3
"""Empaqueta la entrega local existente tras verificar pruebas, alcance y hashes.

No ejecuta pruebas ni instala dependencias. Ejecutar con python -B.
La carpeta entrega/cierre-v1 debe haber sido creada exclusivamente para el lote.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import hashlib
import json
import os
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "entrega/cierre-v1"
ARCHIVOS_PRODUCTO = [
    "critico_cli.py", "probar_todo.py", "critic_i18n.py", "requirements.txt", "LICENSE",
    "03_rubric.yaml", "04_critic.config.yaml", "README_PRODUCTO.md", "LEEME.md",
    "CHANGELOG.md", "LECCIONES_APRENDIDAS.md", "prompts/critico_system.md",
    "locales/es.json", "locales/en.json",
    "01_Manual_completo_del_Critico_v1.0.0.md", "02_FROZEN_v3.3.md",
    "13_Diseno_Completo_Universal_Critico.md",
    "06_migration/v2_to_v3.py", "evals/validators.py", "evals/calibration.py",
    "evals/patterns.py", "evals/calibration_panel.py",
    "scripts/outcome_runner.py", "scripts/verify_freeze.py",
    "scripts/autopopulate_v1_angle.py", "scripts/empaquetar_cierre.py",
    "docs/API_COMPATIBILITY.md", "scripts/package_bilingual.py",
    "05_schema/objection.yaml", "05_schema/triage.yaml", "05_schema/verdict.yaml",
    "05_schema/outcome.yaml", "05_schema/risk_accepted.yaml", "05_schema/skip_incident.yaml",
    "05_schema/pattern.yaml", "05_schema/golden_case.yaml",
    "templates/objection.yaml", "templates/triage.yaml", "templates/verdict.yaml",
    "templates/outcome.yaml", "templates/risk_accepted.yaml", "templates/skip_incident.yaml",
    "templates/pattern.yaml", "skills/critico/SKILL.md", "skills/critico/agents/openai.yaml",
    "skills/critico/references/metodo.md", "skills/critico/references/kuvexta.md",
    "skills/critico/references/formato-salida.md",
]
REPORTES = ["CIERRE.md", "MATRIZ_COBERTURA.csv", "INVENTARIO_ANTES.json",
            "INVENTARIO_DESPUES.json", "RESULTADOS.json", "DEPENDENCIAS.txt"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sin_enlaces(path: Path) -> None:
    for p in [path, *path.parents]:
        if p.is_symlink() or getattr(p, "is_junction", lambda: False)():
            raise RuntimeError(f"GUARDA: enlace o junction {p}")


def inventario() -> dict:
    files = {}
    directories = []
    for root, dirs, names in os.walk(BASE, followlinks=False):
        if Path(root) == BASE:
            dirs[:] = [d for d in dirs if d not in (".entorno-cierre", "entrega")]
        for name in dirs + names:
            sin_enlaces(Path(root) / name)
        directories.extend((Path(root) / d).relative_to(BASE).as_posix() for d in dirs)
        for name in names:
            path = Path(root) / name
            files[path.relative_to(BASE).as_posix()] = sha(path)
    return {"files": files, "directories": sorted(directories)}


def comprobar_alcance() -> dict:
    sin_enlaces(BASE)
    sin_enlaces(OUT)
    before = json.loads((OUT / "INVENTARIO_ANTES.json").read_text(encoding="utf-8"))
    proposal_path = BASE / "propuestas/CIERRE-CRITICO-01.json"
    if sha(proposal_path) != "4b38d0306dc7af267d79324ef743c0839469bf81ff741029da6d6bcdb0149c56":
        raise RuntimeError("GUARDA: propuesta distinta")
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    editable = set(proposal["archivos_editables"])
    new = set(proposal["archivos_nuevos"])
    current = inventario()
    changed = []
    for name, digest in before["files"].items():
        if name not in current["files"]:
            raise RuntimeError(f"GUARDA: archivo previo ausente: {name}")
        if current["files"][name] != digest:
            if name not in editable:
                raise RuntimeError(f"GUARDA: cambio fuera del alcance: {name}")
            changed.append(name)
    created = set(current["files"]) - set(before["files"])
    if not created <= new:
        raise RuntimeError(f"GUARDA: archivos nuevos fuera del alcance: {created - new}")
    permitted_dirs = set(before["directories"])
    for name in new:
        permitted_dirs.update(p.as_posix() for p in Path(name).parents if str(p) != ".")
    unexpected_dirs = set(current["directories"]) - permitted_dirs
    if unexpected_dirs:
        raise RuntimeError(f"GUARDA: directorios inesperados o temporales remanentes: {unexpected_dirs}")
    for directory in before["directories"]:
        if directory not in current["directories"]:
            raise RuntimeError(f"GUARDA: directorio previo ausente: {directory}")
    current.update(fecha="2026-10-26", cambios=sorted(changed), nuevos=sorted(created),
                   caches_previos_preservados=True,
                   limite="Comparacion de contenido y directorios al inicio/final; no monitor continuo del sistema")
    return current


def main() -> None:
    current = comprobar_alcance()
    results = json.loads((OUT / "RESULTADOS.json").read_text(encoding="utf-8"))
    last = results["ciclos"][-1]
    if last["exit_code"] != 0 or last["resumen"]["fallidas"] != 0:
        raise RuntimeError("Pruebas finales fallidas")
    if not last.get("fuentes"):
        raise RuntimeError("Faltan hashes de fuentes de la corrida final")
    for name in ARCHIVOS_PRODUCTO:
        if sha(BASE / name) != last["fuentes"].get(name):
            raise RuntimeError(f"Fuente cambio despues de pruebas: {name}")
    for check in results.get("verificaciones", []):
        if check["exit_code"] != 0:
            raise RuntimeError("Verificacion adicional fallida")
    if not any(c.get("tipo") == "skill" for c in results.get("verificaciones", [])):
        raise RuntimeError("Falta validacion estructural de skill")
    inv = OUT / "INVENTARIO_DESPUES.json"
    inv.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{inv.name}: {sha(inv)}")
    entries = {name: BASE / name for name in ARCHIVOS_PRODUCTO}
    entries.update({"entrega/" + name: OUT / name for name in REPORTES})
    for run in results["ciclos"] + results.get("verificaciones", []):
        log = BASE / run["log"]
        sin_enlaces(log)
        if not log.resolve().is_relative_to((OUT / "logs").resolve()) or sha(log) != run["sha256_log"]:
            raise RuntimeError("Log fuera de destino o con hash distinto")
        entries["entrega/logs/" + log.name] = log
    manifest = {"formato": "critico-cierre-v1", "fecha": "2026-10-26",
                "sha256": {name: sha(p) for name, p in sorted(entries.items())},
                "nota": "El manifiesto no se incluye en su propia lista de hashes. El SHA-256 del ZIP se informa al generar."}
    mf = OUT / "MANIFIESTO_SHA256.json"
    mf.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entries["entrega/MANIFIESTO_SHA256.json"] = mf
    archive = OUT / "critico-cierre-v1.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for name, p in sorted(entries.items()):
            sin_enlaces(p)
            z.write(p, name)
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(entries) or z.testzip() is not None:
            raise RuntimeError("ZIP incompleto o corrupto")
        for name, digest in manifest["sha256"].items():
            if hashlib.sha256(z.read(name)).hexdigest() != digest:
                raise RuntimeError(f"Contenido ZIP distinto: {name}")
        if z.read("entrega/MANIFIESTO_SHA256.json") != mf.read_bytes():
            raise RuntimeError("Manifiesto ZIP distinto")
    # El empaquetado tampoco puede alterar fuentes, caches ni temporales previos.
    comprobar_alcance()
    print(f"ZIP_VERIFICADO {archive}\nARCHIVOS={len(entries)}\nSHA256={sha(archive)}\nMANIFIESTO_SHA256={sha(mf)}")


if __name__ == "__main__":
    main()

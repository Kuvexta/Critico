#!/usr/bin/env python3
"""Entrega documental AUTORIA-LICENCIAS-01; no instala ni elige licencias.

Uso: python -B -X utf8 scripts/empaquetar_licencias.py --comprobar
     python -B -X utf8 scripts/empaquetar_licencias.py
Conserva cierre-v1 y crea un ZIP nuevo exclusivamente. Sin extraccion a disco.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import csv
import hashlib
import io
import json
import os
import zipfile
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "entrega/licencias-v1"
OLD_ZIP = BASE / "entrega/cierre-v1/critico-cierre-v1.zip"
OLD_SHA = "da0f6bd2d38efadd2c7fd212d567f7788b787127611800c58dd0b4c01648967f"
PROPOSAL_SHA = "32a1a2d67234144bc664b431aef89b49fc194c59a7dd4bf6cc5d19e4ae7b80eb"
LICENSE_IDS = {"MIT", "Apache-2.0", "MPL-2.0", "GPL-3.0-only", "AGPL-3.0-only", "CC-BY-4.0", "CC-BY-SA-4.0"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verificar_ruta(path: Path) -> None:
    for part in [path, *path.parents]:
        if part.is_symlink() or getattr(part, "is_junction", lambda: False)():
            raise RuntimeError(f"GUARDA: enlace o junction: {part}")


def inventario() -> dict:
    files, dirs_found = {}, []
    for current, dirs, names in os.walk(BASE, followlinks=False):
        # Solo se excluyen las salidas propias; entorno y cierre-v1 SI se verifican.
        dirs[:] = [d for d in dirs if Path(current) / d != OUT]
        for name in dirs + names:
            verificar_ruta(Path(current) / name)
        dirs_found.extend((Path(current) / d).relative_to(BASE).as_posix() for d in dirs)
        for name in names:
            p = Path(current) / name
            files[p.relative_to(BASE).as_posix()] = sha(p.read_bytes())
    return {"files": files, "directories": sorted(dirs_found)}


def comprobar() -> tuple[dict, dict, dict[str, bytes]]:
    verificar_ruta(BASE)
    verificar_ruta(OUT)
    proposal_file = BASE / "propuestas/AUTORIA-LICENCIAS-01.json"
    if sha(proposal_file.read_bytes()) != PROPOSAL_SHA:
        raise RuntimeError("GUARDA: propuesta distinta")
    proposal = json.loads(proposal_file.read_text(encoding="utf-8"))
    before = json.loads((OUT / "INVENTARIO_ANTES.json").read_text(encoding="utf-8"))
    if before["propuesta_sha256"] != PROPOSAL_SHA or before["zip_anterior_sha256"] != OLD_SHA:
        raise RuntimeError("GUARDA: baseline inesperado")
    editable = set(proposal["archivos_editables"])
    added = set(proposal["archivos_nuevos"])
    current = inventario()
    changes = []
    for name, digest in before["files"].items():
        if name not in current["files"]:
            raise RuntimeError(f"GUARDA: archivo previo ausente: {name}")
        if current["files"][name] != digest:
            if name not in editable:
                raise RuntimeError(f"GUARDA: archivo fuera de alcance modificado: {name}")
            changes.append(name)
    new_files = set(current["files"]) - set(before["files"])
    if new_files != added:
        raise RuntimeError(f"GUARDA: nuevos faltantes o no autorizados: {new_files ^ added}")
    expected_dirs = set(before["directories"])
    for name in added:
        expected_dirs.update(p.as_posix() for p in PurePosixPath(name).parents if str(p) != ".")
    if set(current["directories"]) != expected_dirs:
        raise RuntimeError("GUARDA: directorios ausentes o inesperados")
    allowed_outputs = {"INVENTARIO_ANTES.json", "INVENTARIO_DESPUES.json", "INFORME.md",
                       "MANIFIESTO_SHA256.json", "critico-con-opciones-licencia-v1.zip"}
    for p in OUT.iterdir():
        verificar_ruta(p)
        if not p.is_file() or p.name not in allowed_outputs:
            raise RuntimeError(f"GUARDA: salida inesperada {p}")

    if sha(OLD_ZIP.read_bytes()) != OLD_SHA:
        raise RuntimeError("GUARDA: ZIP anterior distinto")
    with zipfile.ZipFile(OLD_ZIP) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or z.testzip() is not None:
            raise RuntimeError("ZIP anterior con duplicados o corrupcion")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise RuntimeError("ZIP anterior con ruta inesperada")
        original = {name: z.read(name) for name in names}
    old_manifest = json.loads(original["entrega/MANIFIESTO_SHA256.json"])
    for name, digest in old_manifest["sha256"].items():
        if name not in original or sha(original[name]) != digest:
            raise RuntimeError(f"Contenido anterior distinto: {name}")
    # Todo componente de producto ya ensayado conserva bytes salvo tres documentos.
    for name, data in original.items():
        if not name.startswith("entrega/") and name not in editable:
            if (BASE / name).read_bytes() != data:
                raise RuntimeError(f"GUARDA: componente ensayado distinto: {name}")
    # LICENSE conserva byte por byte el texto anterior y solo agrega una nota.
    if not (BASE / "LICENSE").read_bytes().startswith(original["LICENSE"]):
        raise RuntimeError("GUARDA: LICENSE previo no preservado como prefijo exacto")
    for name in ["AUTORIA.md", "LICENSE", "README_PRODUCTO.md"]:
        if "Autor del proyecto: KUVEXTA GROUP" not in (BASE / name).read_text(encoding="utf-8"):
            raise RuntimeError(f"Falta autoria en {name}")
    selection = json.loads((BASE / "licencias/DECISION_PENDIENTE.json").read_text(encoding="utf-8"))
    if selection["seleccion_futura"] is not None or selection["activada"] is not False:
        raise RuntimeError("GUARDA: licencia futura activada sin autorizacion")
    sources = selection["fuentes"]
    if len(sources) != 7 or {s["spdx"] for s in sources} != LICENSE_IDS:
        raise RuntimeError("Catalogo estandar incompleto")
    for s in sources:
        if s["archivo"] != f"licencias/referencia/{s['spdx']}.txt":
            raise RuntimeError("Referencia con ruta distinta")
        if not s["url"].startswith("https://raw.githubusercontent.com/spdx/license-list-data/"):
            raise RuntimeError("Origen de referencia inesperado")
        data = (BASE / s["archivo"]).read_bytes()
        if sha(data) != s["sha256"] or len(data) != s["bytes"]:
            raise RuntimeError("Referencia distinta de la descargada")
    with (BASE / "licencias/COMPARATIVA.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 10 or {r["opcion"] for r in rows} != LICENSE_IDS | {"PROPIETARIA-COMERCIAL", "SOURCE-AVAILABLE", "DOBLE-LICENCIA"}:
        raise RuntimeError("Comparativa incompleta")
    compile(Path(__file__).read_text(encoding="utf-8"), str(__file__), "exec")
    for name in added:
        if name.endswith(".md"):
            text = (BASE / name).read_text(encoding="utf-8")
            # Verificar enlaces relativos simples de los documentos nuevos.
            import re
            for ref in re.findall(r"\]\(([^)]+)\)", text):
                if not ref.startswith(("http://", "https://", "#")):
                    dest = (BASE / name).parent / ref.split("#", 1)[0]
                    if not dest.is_file():
                        raise RuntimeError(f"Referencia local inexistente: {name}: {ref}")
    current.update(fecha="2026-10-27", cambios=sorted(changes), nuevos=sorted(new_files),
                   zip_anterior_sha256=OLD_SHA, codigo_previo_preservado=True,
                   entorno_y_caches_previos_preservados=True,
                   limite="Comparacion de contenido y directorios, no monitor continuo de llamadas del sistema")
    return proposal, current, original


def empaquetar() -> None:
    proposal, current, original = comprobar()
    archive = OUT / "critico-con-opciones-licencia-v1.zip"
    if archive.exists():
        raise RuntimeError("GUARDA: destino ZIP ya existe; no se sobrescribe")
    before_bytes = (OUT / "INVENTARIO_ANTES.json").read_bytes()
    after = OUT / "INVENTARIO_DESPUES.json"
    after.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entries = dict(original)
    for name in proposal["archivos_editables"] + proposal["archivos_nuevos"]:
        entries[name] = (BASE / name).read_bytes()
    for name in ["INVENTARIO_ANTES.json", "INVENTARIO_DESPUES.json", "INFORME.md"]:
        entries["entrega/licencias-v1/" + name] = (OUT / name).read_bytes()
    manifest = {"formato": "critico-con-opciones-licencia-v1", "fecha": "2026-10-27",
                "autor_proyecto": "KUVEXTA GROUP", "licencia_futura_activada": False,
                "propuesta_sha256": PROPOSAL_SHA, "zip_anterior_sha256": OLD_SHA,
                "sha256": {name: sha(data) for name, data in sorted(entries.items())},
                "nota": "Este es el manifiesto vigente del paquete documental. entrega/MANIFIESTO_SHA256.json se conserva como evidencia HISTORICA del ZIP anterior. El manifiesto vigente no se hashea a si mismo; el SHA-256 del ZIP se informa al finalizar."}
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    entries["entrega/licencias-v1/MANIFIESTO_SHA256.json"] = manifest_bytes
    # Ensamblar en memoria, sin extraccion ni temporales en el sistema.
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(entries.items()):
            z.writestr(name, data)
    payload = buf.getvalue()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        if z.testzip() is not None or len(z.namelist()) != len(entries) or set(z.namelist()) != set(entries):
            raise RuntimeError("Paquete en memoria inconsistente")
        for name, digest in manifest["sha256"].items():
            if sha(z.read(name)) != digest:
                raise RuntimeError(f"Hash de entrada distinto: {name}")
    # Antes de persistir, comprobar ausencia de cambios concurrentes.
    _, again, _ = comprobar()
    if again != current or (OUT / "INVENTARIO_ANTES.json").read_bytes() != before_bytes:
        raise RuntimeError("GUARDA: cambio concurrente detectado")
    for name, data in entries.items():
        if name in proposal["archivos_editables"] + proposal["archivos_nuevos"]:
            if (BASE / name).read_bytes() != data:
                raise RuntimeError("GUARDA: fuente cambio durante empaquetado")
    mf = OUT / "MANIFIESTO_SHA256.json"
    mf.write_bytes(manifest_bytes)
    with archive.open("xb") as f:
        f.write(payload)
    if sha(archive.read_bytes()) != sha(payload) or mf.read_bytes() != manifest_bytes:
        raise RuntimeError("Verificacion de escritura fallida")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise RuntimeError("ZIP en disco corrupto")
        for name, data in entries.items():
            if z.read(name) != data:
                raise RuntimeError(f"Entrada en disco distinta: {name}")
    _, final, _ = comprobar()
    if final != current:
        raise RuntimeError("GUARDA: cambio concurrente tras escritura")
    print(f"ZIP_VERIFICADO {archive}\nARCHIVOS={len(entries)}\nSHA256={sha(archive.read_bytes())}")
    for p in [after, OUT / "INFORME.md", mf]:
        print(f"{p.name} SHA256={sha(p.read_bytes())}")
    print("CODIGO_ENTORNO_CACHES_Y_PAQUETE_ANTERIOR_PRESERVADOS; LICENCIA_FUTURA_NO_ACTIVADA")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comprobar", action="store_true", help="solo verificaciones, sin escribir salidas")
    args = parser.parse_args()
    if args.comprobar:
        _, current, _ = comprobar()
        print(f"COMPROBACION_OK: {len(current['cambios'])} documentos modificados, {len(current['nuevos'])} archivos nuevos")
    else:
        empaquetar()


if __name__ == "__main__":
    main()

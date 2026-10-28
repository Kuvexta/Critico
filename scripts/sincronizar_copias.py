#!/usr/bin/env python3
"""Reconciliador de copias del ecosistema Kuvexta (GitOps en miniatura).

Metodología (OpenGitOps): el repositorio público es el estado DESEADO
(declarativo, versionado e inmutable); este agente hace PULL automático del
estado deseado y RECONCILIA las copias locales (producción y workspace) de
forma continua e idempotente (aplicar dos veces es seguro).

Flujo por ejecución:
  1. (--pull) git fetch + merge --ff-only en el clon local (falla ruidoso
     si hay divergencia: nunca reescribe historia).
  2. Compara cada archivo rastreado por git contra cada destino (SHA-256).
  3. (--aplicar) copia los que faltan o difieren. Sin --aplicar = dry-run.
  4. (--log) anexa una línea JSONL con el resultado (auditoría).
  5. (--bup) además sincroniza el espejo curado de BUP en D:\\.

No borra nada de los destinos (los extras locales se conservan; los borrados
los hace Andrés por ítem con hash y acta).

Uso:
  PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/sincronizar_copias.py                 # dry-run
  PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/sincronizar_copias.py --aplicar        # aplica
  PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/sincronizar_copias.py --pull --aplicar --log r.jsonl --bup
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DESTINOS = [
    Path("/mnt/d/KUVEXTA_REPOS/Critico"),          # producción
    Path("/mnt/d/Downloads/Temporales_20261026"),  # workspace privado
]
BUP_CLONE = Path("/home/holding/kuvexta/bup")
BUP_ESPEJO = Path("/mnt/d/KUVEXTA_REPOS/BUP")
# Espejo curado de BUP: (archivo en el repo BUP, archivo en el espejo D:\)
BUP_MAPEO = [
    ("README.md", "README.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("POLITICA_DOCUMENTACION_v2.1.md", "POLITICA_DOCUMENTACION_v2.1.md"),
    ("docs/INSTALACION.md", "INSTALACION.md"),
    ("docs/diseno/", "diseno/"),
]


def git_pull_fast_forward(clone: Path) -> str:
    r1 = subprocess.run(["git", "fetch", "origin"], cwd=clone, capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(f"git fetch falló: {r1.stderr.strip()}")
    r2 = subprocess.run(["git", "merge", "--ff-only", "origin/main"], cwd=clone, capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(f"git merge --ff-only falló (divergencia): {r2.stderr.strip()}")
    return r2.stdout.strip() or "sin cambios"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sincronizar_arbol(origen: Path, lista: list[str], destino: Path) -> dict:
    faltan, drift, copiados = [], [], 0
    for f in lista:
        src = origen / f
        if not src.is_file():
            continue
        dst = destino / f
        if not dst.exists():
            faltan.append(f)
        elif sha(dst) != sha(src):
            drift.append(f)
        else:
            continue
        if aplicar:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copiados += 1
    return {"faltan": len(faltan), "drift": len(drift), "copiados": copiados,
            "faltan_lista": faltan, "drift_lista": drift}


def sincronizar_bup() -> dict:
    faltan, drift, copiados = [], [], 0
    for src_rel, dst_rel in BUP_MAPEO:
        src = BUP_CLONE / src_rel
        if src.is_dir():
            for f in sorted(src.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(src)
                dst = BUP_ESPEJO / dst_rel / rel
                if not dst.exists() or sha(dst) != sha(f):
                    faltan.append(str(dst_rel / rel))
                    if aplicar:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dst)
                        copiados += 1
        elif src.is_file():
            dst = BUP_ESPEJO / dst_rel
            if not dst.exists() or sha(dst) != sha(src):
                faltan.append(dst_rel)
                if aplicar:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    copiados += 1
    return {"faltan": len(faltan), "drift": len(drift), "copiados": copiados,
            "faltan_lista": faltan, "drift_lista": drift}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="copia los archivos con drift/faltantes")
    ap.add_argument("--pull", action="store_true", help="git fetch + merge --ff-only antes de sincronizar")
    ap.add_argument("--bup", action="store_true", help="sincroniza también el espejo curado de BUP")
    ap.add_argument("--log", help="anexa una línea JSONL de auditoría a este archivo")
    ap.add_argument("--destino", action="append", help="destino adicional")
    global aplicar
    args = ap.parse_args()
    aplicar = args.aplicar

    if not args.aplicar:
        print("DRY-RUN (sin cambios). Usa --aplicar para sincronizar.\n")

    registro = {"ts": datetime.now(timezone.utc).isoformat(), "modo": "aplicar" if args.aplicar else "dry-run"}
    salida = 0

    if args.pull:
        try:
            registro["pull"] = git_pull_fast_forward(REPO)
            print(f"pull: {registro['pull']}")
        except RuntimeError as e:
            print(f"PULL FAIL: {e}")
            return 2

    if not (REPO / ".git").exists():
        print("FAIL: el origen debe ser el clon del repositorio (con .git).")
        return 2

    destinos = list(DESTINOS)
    if args.destino:
        destinos += [Path(d) for d in args.destino]

    lista = [l for l in subprocess.run(["git", "ls-files"], cwd=REPO,
                                       capture_output=True, text=True).stdout.splitlines() if l.strip()]
    registro["destinos"] = {}
    for destino in destinos:
        if not destino.exists():
            print(f"SKIP: destino inexistente: {destino}")
            continue
        r = sincronizar_arbol(REPO, lista, destino)
        registro["destinos"][str(destino)] = {k: v for k, v in r.items() if not k.endswith("_lista")}
        print(f"{destino}: faltan {r['faltan']} · drift {r['drift']}"
              + (f" · copiados {r['copiados']}" if args.aplicar else ""))
        for f in r["faltan_lista"]:
            print(f"    FALTA {f}")
        for f in r["drift_lista"]:
            print(f"    DRIFT {f}")
        if r["faltan"] or r["drift"]:
            salida = 1

    if args.bup:
        r = sincronizar_bup()
        registro["bup_espejo"] = {k: v for k, v in r.items() if not k.endswith("_lista")}
        print(f"{BUP_ESPEJO} (BUP): faltan {r['faltan']} · copiados {r['copiados']}")
        for f in r["faltan_lista"]:
            print(f"    FALTA {f}")
        if r["faltan"]:
            salida = 1

    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        print(f"log: {args.log}")

    if salida == 1 and args.aplicar:
        salida = 0  # deriva corregida: ciclo sano
    return salida


if __name__ == "__main__":
    sys.exit(main())

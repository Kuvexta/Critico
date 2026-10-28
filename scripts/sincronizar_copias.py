#!/usr/bin/env python3
"""Sincroniza las copias de trabajo del Crítico desde el repositorio (clon local).

Origen canónico: el clon local del repositorio público (rama main).
Destinos: la copia de producción y el workspace privado (rutas configurables).

Reglas:
- Copia SOLO los archivos rastreados por git (git ls-files), byte a byte
  (SHA-256) cuando difieren o faltan.
- No borra nada del destino (los extras de cada copia se conservan; los
  borrados los hace Andrés por ítem con hash y acta).
- Sin --aplicar solo informa (dry-run); con --aplicar copia.

Uso:
  PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/sincronizar_copias.py            # dry-run
  PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/sincronizar_copias.py --aplicar  # sincroniza
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DESTINOS = [
    Path("/mnt/d/KUVEXTA_REPOS/Critico"),          # producción
    Path("/mnt/d/Downloads/Temporales_20261026"),  # workspace privado
]


def archivos_rastreados() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True)
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="copia los archivos con drift/faltantes")
    ap.add_argument("--destino", action="append", help="destino adicional")
    args = ap.parse_args()

    if not (REPO / ".git").exists():
        print("FAIL: el origen debe ser el clon del repositorio (con .git).")
        return 2
    if not args.aplicar:
        print("DRY-RUN (sin cambios). Usa --aplicar para sincronizar.\n")

    destinos = list(DESTINOS)
    if args.destino:
        destinos += [Path(d) for d in args.destino]

    salida = 0
    for destino in destinos:
        faltan, drift, copiados = [], [], 0
        if not destino.exists():
            print(f"SKIP: destino inexistente: {destino}")
            continue
        for f in archivos_rastreados():
            src = REPO / f
            if not src.is_file():
                continue
            rh = hashlib.sha256(src.read_bytes()).hexdigest()
            dst = destino / f
            if not dst.exists():
                faltan.append(f)
            elif hashlib.sha256(dst.read_bytes()).hexdigest() != rh:
                drift.append(f)
            else:
                continue
            if args.aplicar:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copiados += 1
        print(f"{destino}")
        print(f"  faltan: {len(faltan)} · drift: {len(drift)}"
              + (f" · copiados: {copiados}" if args.aplicar else ""))
        for f in faltan:
            print(f"    FALTA {f}")
        for f in drift:
            print(f"    DRIFT {f}")
        if faltan or drift:
            salida = 1
    if not args.aplicar and salida:
        print("\nHay deriva. Revisa y corre con --aplicar.")
    elif not args.aplicar:
        print("\nCopias sincronizadas.")
    return salida


if __name__ == "__main__":
    sys.exit(main())

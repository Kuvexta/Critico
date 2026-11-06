"""Escaneo público como GATE (CRITICO-SKILL-02). El repositorio es PÚBLICO.

Complementa a gitleaks (secretos): busca en los archivos versionados correos,
NIT/cédulas con formato colombiano, IDs internos de gobernanza y nombres
reales. Falla (rc 1) solo ante hallazgos NUEVOS frente a la línea base
`docs/escaneo_publico_baseline.json`, que registra huellas (sha256 de
ruta|regla|coincidencia) y conteos, nunca el texto encontrado.

Nombres reales: además del patrón base, `ESCANEO_NOMBRES="Nombre1,Nombre2"`
añade nombres a buscar sin escribirlos en el repositorio.

Uso:
  python3 -B scripts/escaneo_publico.py                      # gate
  python3 -B scripts/escaneo_publico.py --write-baseline     # solo con decisión registrada en el PR
Si encuentra algo: para, redacta o excluye, y deja constancia en el PR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
BASELINE = BASE / "docs" / "escaneo_publico_baseline.json"
RULES = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}",
    "nit_cedula_co": r"(?<![\d.])\d{1,3}(?:\.\d{3}){2,3}(?:-\d)?(?![\d.])|(?<!\d)\d{9}-\d(?!\d)",
    "id_interno_bz": r"\bBZ-\d{8}-\d{3}\b",
    "id_interno_enc": r"\bENC-[A-Z0-9]{2,}-\d+\b",
    "nombre_real": r"\bAndr[eé]s\b",
}
IGNORED = {"docs/escaneo_publico_baseline.json"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=BASE, capture_output=True, check=True).stdout
    return sorted(n for n in out.decode("utf-8").split("\0") if n and n not in IGNORED)


def rules() -> dict[str, re.Pattern]:
    compiled = {k: re.compile(v) for k, v in RULES.items()}
    extra = [n.strip() for n in os.environ.get("ESCANEO_NOMBRES", "").split(",") if n.strip()]
    if extra:
        compiled["nombre_real_extra"] = re.compile(r"\b(?:" + "|".join(map(re.escape, extra)) + r")\b", re.I)
    return compiled


SKIPPED: list[str] = []  # archivos no legibles como texto UTF-8: se informan, nunca se omiten en silencio


def scan(files: list[str] | None = None) -> Counter:
    found: Counter = Counter()
    SKIPPED.clear()
    for name in files if files is not None else tracked_files():
        path = BASE / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            SKIPPED.append(name)
            continue
        for rule, pattern in rules().items():
            for match in pattern.findall(text):
                fp = hashlib.sha256(f"{name}|{rule}|{match}".encode("utf-8")).hexdigest()
                found[(name, rule, fp)] += 1
    return found


def load_baseline() -> Counter:
    if not BASELINE.exists():
        return Counter()
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    return Counter({(e["path"], e["rule"], e["fingerprint"]): e["count"] for e in data["entries"]})


def baseline_bytes(found: Counter) -> bytes:
    entries = [{"path": p, "rule": r, "fingerprint": f, "count": c} for (p, r, f), c in sorted(found.items())]
    data = {"id": "escaneo-publico-baseline", "note": "Huellas sha256(ruta|regla|coincidencia) de hallazgos preexistentes aceptados; no contiene el texto.",
            "rules": sorted(RULES), "entries": entries}
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def new_findings(found: Counter, baseline: Counter) -> list[tuple[str, str, int]]:
    return [(p, r, c - baseline.get((p, r, f), 0)) for (p, r, f), c in sorted(found.items()) if c > baseline.get((p, r, f), 0)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()
    found = scan()
    if args.write_baseline:
        BASELINE.write_bytes(baseline_bytes(found))
        print(f"BASELINE_ESCRITA: {sum(found.values())} coincidencias en {len({k[0] for k in found})} archivos")
        return 0
    nuevos = new_findings(found, load_baseline())
    if nuevos:
        for path, rule, extra in nuevos:
            print(f"ESCANEO_FALLO: {path}: regla {rule}: {extra} coincidencia(s) nueva(s) (texto no mostrado)")
        return 1
    for name in SKIPPED:
        print(f"ESCANEO_AVISO: no escaneado (no es texto UTF-8): {name}")
    print(f"ESCANEO_OK: {len(tracked_files())} archivos ({len(SKIPPED)} no escaneables, listados arriba); 0 hallazgos nuevos (línea base: {sum(load_baseline().values())})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

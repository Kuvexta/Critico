"""Escaneo público como GATE (CRITICO-SKILL-02). El repositorio es PÚBLICO.

Complementa a gitleaks (secretos): busca en los archivos versionados correos,
NIT/cédulas con formato colombiano, IDs internos de gobernanza y nombres
reales. Falla (rc 1) solo ante hallazgos NUEVOS frente a la línea base
`docs/escaneo_publico_baseline.json`, que registra huellas (sha256 de
ruta|regla|coincidencia) y conteos, nunca el texto encontrado.

Nombres reales: SOLO por entorno, `ESCANEO_NOMBRES="Nombre1,Nombre2"` (en CI, el
secreto del repositorio `ESCANEO_NOMBRES`); nunca se escriben en el código ni se
imprimen. Las demás reglas dan ruta, línea y regla; `nombre_real` da solo el número de
coincidencias (en local, `--detalle` con el secreto en el entorno muestra ruta y línea;
en CI, `--detalle` se rechaza). Sin la variable, la regla `nombre_real` no se aplica y el
gate lo avisa (ESCANEO_AVISO). Las huellas de la línea base son las mismas
(regla `nombre_real`), así que se reutilizan al definir la variable.

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
}
IGNORED = {"docs/escaneo_publico_baseline.json"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=BASE, capture_output=True, check=True).stdout
    return sorted(n for n in out.decode("utf-8").split("\0") if n and n not in IGNORED)


def rules() -> dict[str, re.Pattern]:
    compiled = {k: re.compile(v) for k, v in RULES.items()}
    extra = [n.strip() for n in os.environ.get("ESCANEO_NOMBRES", "").split(",") if n.strip()]
    if extra:
        compiled["nombre_real"] = re.compile(r"\b(?:" + "|".join(map(re.escape, extra)) + r")\b", re.I)
    return compiled


SKIPPED: list[str] = []  # archivos no legibles como texto UTF-8: se informan, nunca se omiten en silencio
LINES: dict[tuple[str, str, str], list[int]] = {}  # huella -> líneas; el texto encontrado NUNCA se guarda ni se imprime


def scan(files: list[str] | None = None) -> Counter:
    found: Counter = Counter()
    SKIPPED.clear()
    LINES.clear()
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
            for m in pattern.finditer(text):
                fp = hashlib.sha256(f"{name}|{rule}|{m.group(0)}".encode("utf-8")).hexdigest()
                found[(name, rule, fp)] += 1
                LINES.setdefault((name, rule, fp), []).append(text.count("\n", 0, m.start()) + 1)
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


def new_locations(found: Counter, baseline: Counter) -> list[tuple[str, int, str]]:
    """(ruta, línea, regla) de cada huella con hallazgos nuevos. Sin texto: así se imprime en CI."""
    out = []
    for (p, r, f), c in sorted(found.items()):
        if c > baseline.get((p, r, f), 0):
            out += [(p, line, r) for line in LINES.get((p, r, f), [])]
    return sorted(set(out))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--detalle", action="store_true",
                        help="solo en local y con ESCANEO_NOMBRES: muestra ruta y línea también para nombre_real")
    args = parser.parse_args()
    if args.detalle and (os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")):
        print("ESCANEO_ERROR: --detalle no se permite en CI (el log es público)")
        return 2
    if args.detalle and not os.environ.get("ESCANEO_NOMBRES", "").strip():
        print("ESCANEO_ERROR: --detalle requiere ESCANEO_NOMBRES en el entorno")
        return 2
    found = scan()
    if args.write_baseline:
        BASELINE.write_bytes(baseline_bytes(found))
        print(f"BASELINE_ESCRITA: {sum(found.values())} coincidencias en {len({k[0] for k in found})} archivos")
        return 0
    nuevos = new_findings(found, load_baseline())
    if nuevos:
        # Solo ruta, línea y regla: la coincidencia (correo, NIT, nombre…) nunca se imprime en claro.
        # Solo ruta, línea y regla; la coincidencia nunca se imprime. Para nombre_real, ni
        # siquiera ruta ni línea (en un log público delatarían el nombre): solo el número,
        # salvo --detalle en local.
        for path, line, rule in new_locations(found, load_baseline()):
            if rule == "nombre_real" and not args.detalle:
                continue
            print(f"ESCANEO_FALLO: {path}:{line}: regla {rule} (coincidencia no mostrada)")
        n_nombres = sum(e for _, r, e in nuevos if r == "nombre_real")
        if n_nombres and not args.detalle:
            print(f"ESCANEO_FALLO: regla nombre_real: {n_nombres} coincidencia(s) nueva(s) (ruta y línea ocultas; "
                  "en local: ESCANEO_NOMBRES=… python3 -B scripts/escaneo_publico.py --detalle)")
        print(f"ESCANEO_FALLO: {sum(e for _, _, e in nuevos)} coincidencia(s) nueva(s); redacta o excluye y deja constancia en el PR")
        return 1
    if not os.environ.get("ESCANEO_NOMBRES", "").strip():
        print("ESCANEO_AVISO: ESCANEO_NOMBRES no definido o vacío (p. ej. PR desde un fork sin secretos); la regla nombre_real no se aplicó")
    for name in SKIPPED:
        print(f"ESCANEO_AVISO: no escaneado (no es texto UTF-8): {name}")
    print(f"ESCANEO_OK: {len(tracked_files())} archivos ({len(SKIPPED)} no escaneables, listados arriba); 0 hallazgos nuevos (línea base: {sum(load_baseline().values())})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

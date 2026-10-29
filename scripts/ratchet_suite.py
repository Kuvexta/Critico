"""Ratchet de la suite histórica (BUP-RATCHET-01, alternativa #9 — engram deadcode-ratchet).

La línea base NUNCA baja en silencio: si el conteo de tests recolectados es
menor que docs/SUITE_BASELINE, el gate FALLA (exit 1). El umbral solo sube:
el mismo cambio que añade tests aprobados sube la línea base.

Simulación del gate (prueba en ambas direcciones): RATCHET_BASELINE=<n>
sobrescribe la línea base sin tocar el archivo (para probar la bajada).
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def baseline() -> int:
    env = os.environ.get("RATCHET_BASELINE")
    if env is not None:
        return int(env)
    return int((BASE / "docs" / "SUITE_BASELINE").read_text(encoding="utf-8").strip())


def collect_count() -> int:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/", "--collect-only", "-q"],
                       cwd=str(BASE), capture_output=True, text=True, timeout=300, env=env)
    if r.returncode != 0:
        print("ratchet: pytest --collect-only falló (el gate no puede verificar el conteo)")
        print(r.stdout[-800:], r.stderr[-800:], file=sys.stderr)
        return -1
    m = re.search(r"(\d+) tests? collected", r.stdout)
    return int(m.group(1)) if m else -1


def main() -> int:
    base = baseline()
    count = collect_count()
    print(f"ratchet suite: recolectados={count} · línea base={base}")
    if count < 0:
        return 1
    if count < base:
        print(f"RATCHET FAIL: el conteo ({count}) está por debajo de la línea base ({base}) — "
              f"bajar el umbral exige PR con justificación y revisión (BUP-RATCHET-01)", file=sys.stderr)
        return 1
    print(f"RATCHET OK: {count} >= {base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

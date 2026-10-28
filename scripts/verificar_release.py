#!/usr/bin/env python3
"""Guarda de release del Crítico (política de documentación v2.1).

Compara VERSION, CHANGELOG, el mapeo de versiones del README y el registro
central docs/HASHES.md. Falla (exit 1) si hay deriva.

Uso: PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verificar_release.py
"""

import hashlib
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

VERSION = (BASE / "VERSION").read_text(encoding="utf-8").strip()
if not re.match(r"^\d{2}\.\d{2}\.\d{2}$", VERSION):
    print(f"FAIL: VERSION inválido: {VERSION}")
    sys.exit(1)

errores = []
readme = (BASE / "README.md").read_text(encoding="utf-8")
changelog = (BASE / "CHANGELOG.md").read_text(encoding="utf-8")

# 1 · mapeo de ejes visible en el README (C2) — metodología leída del config
import yaml as _yaml
cfg = _yaml.safe_load((BASE / "04_critic.config.yaml").read_text(encoding="utf-8"))
critic_v = f"v{cfg['critic_version']}"
if f"`{VERSION}`" not in readme or f"`{critic_v}`" not in readme:
    errores.append(f"README sin el mapeo de versiones (release del repo + metodología {critic_v})")

# 2 · CHANGELOG con entrada para la versión actual
if f"## {VERSION}" not in changelog:
    errores.append(f"CHANGELOG sin entrada para {VERSION}")

# 3 · registro central de hashes: cada fila existe, hash coincide y estado es vigente/aprobado
central = (BASE / "docs" / "HASHES.md").read_text(encoding="utf-8")
for linea in central.splitlines():
    celdas = [c.strip() for c in linea.split("|")]
    if len(celdas) < 5 or not celdas[1] or celdas[1] in ("Documento", "---"):
        continue
    nombre, estado, sha = celdas[1], celdas[2], celdas[3]
    p = BASE / nombre
    if not p.exists():
        errores.append(f"registro central: ruta ausente {nombre}")
        continue
    if hashlib.sha256(p.read_bytes()).hexdigest() != sha:
        errores.append(f"registro central: hash distinto en {nombre}")
    if estado not in ("vigente", "aprobado"):
        errores.append(f"registro central: {nombre} en estado {estado}")

if errores:
    for e in errores:
        print("FAIL:", e)
    sys.exit(1)
print(f"OK: versión {VERSION} consistente en VERSION, README, CHANGELOG y docs/HASHES.md")

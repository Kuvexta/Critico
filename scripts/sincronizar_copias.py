#!/usr/bin/env python3
"""PUNTERO — el reconciliador canónico vive en Kuvexta/Ecosistema.

Este archivo ya no es la implementación: la copia canónica (con --pull,
--log, --bup y configuración por estación) está en
https://github.com/Kuvexta/Ecosistema → herramientas/sincronizar_copias.py.

Uso en esta estación:
  PYTHONDONTWRITEBYTECODE=1 python3 -B /home/holding/kuvexta/ecosistema/herramientas/sincronizar_copias.py [--pull] [--aplicar] [--bup]

(Se conserva este puntero para no borrar archivos: los borrados los hace
Andrés por ítem con hash y acta.)
"""
import sys

def main() -> int:
    print(__doc__)
    return 0

if __name__ == "__main__":
    sys.exit(main())

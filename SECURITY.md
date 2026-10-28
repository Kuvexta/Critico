# Seguridad — reporte de vulnerabilidades

El Crítico es una herramienta de análisis **defensivo** (perfiles de seguridad,
forense, ingeniería inversa y afines). No se autoriza su uso para actividades
ilícitas (dimensión 75 de la rúbrica).

## Reportar una vulnerabilidad

Si encuentras una vulnerabilidad (del CLI, esquemas, validadores o de la
propia metodología), **no la publiques en un issue público**:

1. Usa el mecanismo privado de GitHub: **Security → Advisories → Report a
   vulnerability** en este repositorio, o
2. Contacta al mantenedor (Andrés, KUVEXTA GROUP) por un canal privado.

## Qué incluir

- Versión exacta (release y `critic_version`).
- Pasos para reproducir (sin secretos ni datos reales).
- Impacto estimado y, si la tienes, mitigación propuesta.

## Alcance honesto

- El repositorio **no contiene** registros de gobernanza ni secretos (el
  secreto del canal TOTP vive fuera del repo).
- El producto está en **etapa construcción (00)**: beta honesto, sin
  certificación independiente.

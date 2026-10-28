# Registro de incidentes — Crítico

## INC-20261026-01 — CERRADO (decisión de Andrés, 2026-10-28)

- **Descripción:** durante trabajo previo al lote de cierre se borraron archivos `.pyc` (cachés de Python) fuera del alcance autorizado.
- **Impacto:** nulo en funcionalidad (los `.pyc` son regenerables); la falta fue de alcance, no de datos.
- **Decisión de Andrés (2026-10-28):** cerrar el incidente con lección aprendida. No se retroautoriza el hecho; no implica reabrir entregas anteriores.
- **Lección aprendida:** los borrados se limitan a temporales propios de la corrida autorizada (verificación de ruta absoluta, propiedad y ausencia de enlaces antes de borrar). Los cachés existentes (`__pycache__/`, `*.pyc`) nunca se crean, cambian, borran ni restauran fuera del alcance explícito. La guarda de limpieza de la batería ya exige ruta dentro de la raíz propia de la corrida.
- **Estado:** CERRADO.

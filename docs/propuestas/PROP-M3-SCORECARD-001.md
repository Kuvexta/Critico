# PROP-M3-SCORECARD-001 — Scorecard 5 ejes en el veredicto (31-oct-2026)

**Autorización:** mandato de Andrés «si realizamos los 5 puntos» · **Estado:** aplicada, commit SOLO LOCAL.
**Qué cambia:** `05_schema/verdict.yaml` — propiedad OPCIONAL `scorecard` (5 ejes 0–5; si algún eje < 5 ⇒ `evidence` obligatorio, sub-regla `if/not/then` en `allOf`) · `templates/verdict.yaml` ejemplo. `$id` SIN bump (retrocompatible; `additionalProperties: false` respetado declarando el campo).
**Motivo:** rúbrica lista para el tribunal en sombra (registro interno BZ-20261031-030); alimenta la Opción A con evidencia obligatoria.
**Validación:** 4 escenarios jsonschema (sin scorecard OK · 5/5 OK · 4/5 sin evidence RECHAZADO · 4/5 con evidence OK) · batería 100/100 · `verify_freeze` OK.

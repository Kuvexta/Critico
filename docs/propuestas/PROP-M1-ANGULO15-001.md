# PROP-M1-ANGULO15-001 — Ángulo 15 «Fallos silenciosos» (31-oct-2026)

**Autorización:** mandato de Andrés «si realizamos los 5 puntos» (plan BZ-20261031-028/030) · **Estado:** aplicada, commit SOLO LOCAL (push/merge/tag exigen OK literal).
**Qué cambia:** `critico_cli.py` (tupla 15 en `ANGLES`) · `locales/es.json`+`en.json` (`angle.15.title/question`) · `prompts/critico_system.md`+`critic_system.en.md` (lista 14→15). **No toca:** rúbrica 108 dims, esquemas, máquina de estados, `v1_angle` (máx. 11 histórico).
**Motivo:** patrón «cazador de fallos silenciosos» (catch vacíos, fallbacks peligrosos, excepciones silenciadas, logs manipulados) ausente de los 14 ángulos (registro interno BZ-20261031-030; procedencia confidencial).
**Validación:** batería 100/100 · paridad es/en preservada · `verify_freeze` OK v3.6.0.

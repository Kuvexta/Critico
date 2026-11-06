# PROP-SKILL02-CRITIC370-001 — ¿`critic_version` 3.6.0 → 3.7.0? (06-nov-2026)

**Encargo:** CRITICO-SKILL-02, punto 12. **Estado: DECIDIDA — opción A (Dirección, 06/11/2026, comentario en Kuvexta/Critico#3: «D1 = A: critic_version sigue en 3.6.0; solo VERSION pasa a 01.01.00»). No aplicada:**
`04_critic.config.yaml` sigue en `critic_version: 3.6.0` y nada en PR-0/PR-A/PR-B lo cambia.
**Clasificación si se aprueba:** producto congelado, CAMBIO con freeze.

## La pregunta para Dirección

Los cambios 1–7 de CRITICO-SKILL-02 viven en `skills/critico/` (modo AUTOCONTROL/INDEPENDIENTE, ficha de
independencia, `artifact_binding`, matriz de caso no declarado, precedencia de gates, `control_cost`, scorecard
opcional, referencia de integraciones). ¿Cuentan como **cambio de metodología** (sube `critic_version`) o como
**cambio de producto** en la capa de la skill (sube solo `VERSION`)?

| Opción | Qué implica | Recomendación del autor |
|---|---|---|
| **A — solo producto** (lo aplicado) | `VERSION` 01.01.00; `critic_version` 3.6.0. Coherente con `CONTRIBUTING.md`: la skill es «capa comunitaria, fuera del freeze»; la rúbrica, los esquemas y el config no cambian. | **Recomendada**: no toca nada congelado y es reversible sin CAMBIO. |
| **B — también metodología** | Además, CAMBIO: `critic_version` y `rubric_version` → `3.7.0`; recalcular `config_hash` (convención de CONTRIBUTING, comprobado por `verify_freeze` desde PR-0); `verify_freeze.py` y locales esperan 3.7.0; `02_FROZEN_v3.4.md` registra el cambio; tag `v3.7.0` con literal. | Solo si Dirección decide que el modo/ligadura forma parte del método congelado (p. ej., para que el expediente YAML lo exija). |

Argumento a favor de B: el modo y la ligadura cambian **qué cuenta como GATE B**, que es una regla de gobierno, no
solo de redacción. Argumento en contra: hoy esa regla vive solo en la skill (texto) y en el golden set de contrato;
ningún esquema ni validador la exige. Si se quiere que el validador la exija, eso es un CAMBIO de esquema/
validadores (también con freeze) y debería ser una propuesta propia, no un efecto colateral de esta.

## Si Dirección elige B (pasos, en un PR aparte)

1. `03_rubric.yaml`: `rubric_version: 3.7.0`. `04_critic.config.yaml`: `critic_version: 3.7.0` y `config_hash`
   recalculado (SHA-256 del fichero sin la línea `config_hash:`).
2. `scripts/verify_freeze.py` y `locales/{es,en}.json` («Freeze OK: v3.7.0»).
3. `02_FROZEN_v3.4.md`, `CHANGELOG.md`, `README.md` (mapa de versiones), `docs/HASHES.md`.
4. Suite completa (`probar_todo.py`, `pytest`, `verify_freeze`, `verificar_release`, ratchet, escaneo) con salida real.
5. Tag `v3.7.0` solo con el literal de Dirección.

**Rollback** en cualquier caso: `d23241c` / `v3.6.0`.

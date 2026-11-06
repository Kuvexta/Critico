# PROP-CONFIGHASH-001 — Corrección del `config_hash` de v3.6.0 (06-nov-2026)

**Encargo:** CRITICO-SKILL-02 · PR-0 (rama `task/CRITICO-SKILL-02-0`, base `d23241c` = tag `v3.6.0`).
**Autorización:** literal de Dirección en la sesión del encargo, 06/11/2026: «config_hash: opción A. Autorizo un
CAMBIO mínimo PR-0 […] corregir solo config_hash en 04_critic.config.yaml a
9aabf3a9b34f3b757478d1c73ba312229241dc02760ce77c5530c0a62d9a7406 según la convención de CONTRIBUTING, sin tocar
critic_version ni otro campo; añade a verify_freeze la comprobación de config_hash […]». **Estado:** propuesta en PR,
pendiente de revisión y fusión (no se fusiona, no se taggea).
**Clasificación:** producto (congelado) — CAMBIO con freeze.

## Hallazgo (preflight Fase 0 del encargo)

`tests/test_subprofile_cosecha.py::test_13_config_hash_recalculado_con_convencion_de_contributing` falla en
`d23241c` (165 passed / 1 failed). Reproducción con la convención de CONTRIBUTING (SHA-256 del fichero excluyendo la
línea del propio campo `config_hash:`):

| Commit | `config_hash` declarado | Calculado |
|---|---|---|
| `107a0b2` (v3.5.0) | `797898e6…` | `797898e6…` ✔ |
| `d23241c` (v3.6.0) | `b9532948…` | `9aabf3a9…` ✘ |

Se descartaron variantes (fichero completo, CRLF, campo vacío): ninguna produce `b9532948…`. El CHANGELOG de
v3.6.0 lo declaraba «recalculado», pero `verify_freeze.py` no comprobaba este campo, por eso pasó.

## Qué cambia

- `04_critic.config.yaml`: **solo** la línea `config_hash` → `9aabf3a9b34f3b757478d1c73ba312229241dc02760ce77c5530c0a62d9a7406`.
  `critic_version` sigue en `3.6.0`; ningún otro campo cambia.
- `scripts/verify_freeze.py`: nueva comprobación que recalcula `config_hash` con la convención de CONTRIBUTING y
  falla si no coincide (prueba de mutación: con el valor viejo devuelve rc 1 y el mensaje con ambos hashes).
- `CHANGELOG.md`: entrada de la corrección. `docs/HASHES.md`: filas regeneradas de los documentos tocados.

**No toca:** `03_rubric.yaml`, `05_schema/`, `evals/validators.py`, `critic_version`, `VERSION`, tags.

## Validación

`probar_todo.py`, `pytest tests/ -v` (incluye `test_13`), `verify_freeze.py`, `verificar_release.py`,
`ratchet_suite.py` — salida real adjunta en el PR.

## Rollback

Revertir el commit del PR (vuelve a `d23241c` / `v3.6.0`). El tag `v3.6.0` no se modifica.

## Efecto en el encargo

Tras fusionar PR-0, el preflight 0.a espera `config_hash 9aabf3a9…` (no `b9532948…`).

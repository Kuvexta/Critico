# PROP-COSECHA-001 — CAMBIO del sub-perfil `ops.cosecha` (Crítico, aditivo v3.5.0)

- **id:** PROP-COSECHA-001
- **titulo:** Sub-perfil `ops.cosecha` (padre `ops`) con 13 dimensiones mapeadas a IDs REALES de la rúbrica v3.4.0 + parámetros del dominio `prc` (pointer_enforcement_strict, snapshot_hash_validation, matriz P29 con BYPASS)
- **estado:** EJECUTADA (2026-10-30)
- **propuesto y ejecutado por:** subagente KUVEXTA (identidad compartida) — encargo autorizado por Andrés
- **ref. diseño:** `Diseno_Catalogo_Gestion_Procesos_20261030_v7.md` §14.5 · `_v6.md` §2/§6.4 · `_v5.md` §2.2/§5 · `_v3.md` §5/§6 (bundle completo)

## Autorización

Literal del cambio: **«te doy autorización para que ejecutes todo hasta el final»** — Andrés, mandato global **BZ-20261030-136** (2026-10-30). Ese mandato cubre propuesta, implementación, verificación, commit **y push** (registrado en el mensaje del commit y en el informe de entrega).

**No se inventa «OK <8hex>»:** la frase canónica del playbook `MUTACIONES.md` no fue emitida para esta propuesta; se registra el mandato global como el literal del cambio. El **hash del diff** se documenta abajo como referencia de integridad (no como autorización).

## Bundle (mapeo C01–C13 a IDs reales, rúbrica v3.4.0)

| Slot | Nombre | ID real | Act | Severidad |
|---|---|---|---|---|
| C01 | Evidencia suficiente | 30 `evidence_quality` | core | Bloqueante |
| C02 | No-inferioridad | 3 `consistency` — **COMPUESTO**: consistencia ∧ no-inferioridad con δ; replay comparativo como evidencia separada (NO alias) | core | Bloqueante |
| C03 | Elegibilidad de replay | 32 `reproducibility` | opt | Bloqueante |
| C04 | Dedup P20 | 100 `duplication` | opt | Bloqueante |
| C05 | Linaje y hashes | 50 `provenance` | core | Bloqueante |
| C06 | Contrato de salida | 9 `contract_compliance` | core | Bloqueante |
| C07 | Clasificación H6/P14 | 88 `secrets_management` **+** 57 `pii_handling` — **AND**: ambas bloqueantes, reporte separado | core | Bloqueante |
| C08 | Idioma P27 | 44 `i18n_l10n` | dom | Bloqueante |
| C09 | Transición de estado | 55 `schema_evolution` | dom | Bloqueante |
| C10 | Precondición de skill | 41 `requirement_fit` — solo skills | core | Bloqueante |
| C11 | Diversidad de contextos | 23 `scalability` — bloqueante si tipo ∈ {SKILL_*}; advisory si tipo ∈ {PROMPT_CANONICO, DEGRADAR} | opt | Condicional |
| C12 | Calibración del perfil | 79 `eval_coverage` — Advisory→Bloqueante si surprise_rate sale de banda (Beta/Wilson, n_min_baseline=50, baseline rodante 4 semanas, `baseline_version`) | opt | Advisory |
| C13 | Impacto en ramas vivas | 17 `blast_radius` **+** 106 `second_order_effects` — advisory; C12/C13 escalan por separado, cada una con su `baseline_version` | core | Advisory |

Parámetros: `domain: prc` · `pointer_enforcement_strict: true` · `snapshot_hash_validation: true` · matriz **P29 binaria** (ficha obligatoria si recurrente ∨ multi-agente ∨ toca canónicos; si no → **BYPASS** automático registrado).

## Archivos

- `04_critic.config.yaml` — `critic_version` 3.4.0→3.5.0 · sub-perfil `ops.cosecha` en `profiles.universals.ops.sub_profiles` · sección nueva `cosecha_prc` (domain, flags estrictos, matriz P29, slots C01–C13 con composición/severidades) · flag `critic.cosecha_prc` · `config_hash` recalculado.
- `03_rubric.yaml` — `rubric_version` 3.4.0→3.5.0 (dimensiones intactas).
- `scripts/verify_freeze.py` — versión esperada 3.5.0 + checks del sub-perfil.
- `locales/es.json`, `locales/en.json` — mensaje «Freeze OK: v3.5.0 …».
- `docs/guia_subperfil_ops_cosecha.md` — **NUEVO**: guía del sub-perfil (bundle completo).
- `tests/test_subprofile_cosecha.py` — **NUEVO**: 13 tests que cubren el cambio (FROZEN §8.4).
- `02_FROZEN_v3.4.md` — §2/§3/§5.1/§6/§9/§10 + nota del cambio.
- `CHANGELOG.md` — entrada v3.5.0 · `README.md` — mapeo de versiones · `docs/HASHES.md` · `docs/SUITE_BASELINE` (153→166).

## No toca

Máquina de estados · 6 macro-perfiles (U2) · `05_schema/*.yaml` (los 8 esquemas y sus `$id` intactos) · `evals/validators.py` (hash congelado intacto) · 34 invariantes · tabla BZ-109 · `probar_todo.py` · `01_Manual`, `13_Diseno`, `docs/en/*` (históricos).

## Validación

`python3 -B -X utf8 probar_todo.py` → 100/0/0 · `python3 -m pytest tests/ -v` → 166 passed (153 históricos + 13 nuevos) · `scripts/verify_freeze.py` OK v3.5.0 · `scripts/verificar_release.py` OK · ratchet 166 ≥ 166 · push verificado con `git rev-parse origin/main`.

## Hash del diff (referencia)

SHA-256 del diff completo del CAMBIO (diff staged contra HEAD) excluyendo este
mismo fichero de propuesta y el registro `docs/HASHES.md` (que contienen el
hash, para evitar circularidad):

```
git diff --cached HEAD -- . \
  ':(exclude)docs/propuestas/PROP-COSECHA-001.md' \
  ':(exclude)docs/HASHES.md' | sha256sum
```

→ `ef1381048c7ef97702020d0cc42de86317fa163469a5bd5da438db9ee3140165`

# Guía del sub-perfil `ops.cosecha` — Crítico v3.5.0

> **CAMBIO:** PROP-COSECHA-001 · autorización: mandato global de Andrés
> («te doy autorización para que ejecutes todo hasta el final»,
> **BZ-20261030-136**, 2026-10-30) · aditivo, no descongela.
> Fuente de diseño: `Diseno_Catalogo_Gestion_Procesos_20261030_v3.md` §5/§6
> (mapeo real) + `_v4.md` §5 (composición) + `_v5.md` §2.2/§5 (C02 compuesto,
> C12/C13 Wilson) + `_v6.md` §2 (frontera motor≠perfil).

## 1. Identidad

- **ID:** `ops.cosecha` · **padre:** macro-perfil `ops` (U2 intacto: los 6
  macro-perfiles no cambian).
- **Dominio:** `prc` (procesos P-PRC). La rúbrica especializada aplica **solo**
  al dominio `procesos`; `prompts` y `agentes` exigen su propio mapeo vía
  CAMBIO (frontera v6 §2, anti-P20).
- **Estrecho a propósito:** 13 slots (15 IDs) — ampliarlo exige nuevo CAMBIO,
  no ajuste de config.

## 2. Mapeo C01–C13 (IDs REALES de la rúbrica v3.4.0)

| Slot | Dimensión(es) | Act | Severidad | Composición |
|---|---|---|---|---|
| C01 | 30 `evidence_quality` | core | Bloqueante | — |
| C02 | 3 `consistency` | core | Bloqueante | **COMPUESTO** (ver §3) |
| C03 | 32 `reproducibility` | opt | Bloqueante | — |
| C04 | 100 `duplication` | opt | Bloqueante | — |
| C05 | 50 `provenance` | core | Bloqueante | — |
| C06 | 9 `contract_compliance` | core | Bloqueante | — |
| C07 | 88 `secrets_management` **+** 57 `pii_handling` | core | Bloqueante | **AND** (ver §4) |
| C08 | 44 `i18n_l10n` | dom | Bloqueante | — |
| C09 | 55 `schema_evolution` | dom | Bloqueante | — |
| C10 | 41 `requirement_fit` | core | Bloqueante | Solo skills |
| C11 | 23 `scalability` | opt | Condicional | Ver §5 |
| C12 | 79 `eval_coverage` | opt | Advisory | Escalado Wilson (§6) |
| C13 | 17 `blast_radius` **+** 106 `second_order_effects` | core | Advisory | Escalado Wilson (§6) |

## 3. C02 — compuesto, NO alias

`no_inferiority` **no es alias** de la dimensión 3 (`consistency`). C02 =
**consistencia ∧ no-inferioridad con δ**: la propuesta debe ser consistente
consigo misma y con el sistema, **y además** demostrar que no es inferior al
incumbente con una δ declarada. La comparación exige **replay comparativo como
evidencia separada, siempre** (v5 §2.2).

## 4. C07 — AND con reporte separado

88 y 57 son **dos dimensiones independientes activas, ambas bloqueantes
(AND)**. El fallo de cualquiera bloquea; se **reportan por separado** (un
hallazgo de secretos no se diluye en uno de PII, ni al revés).

## 5. C11 — severidad condicional (en config)

`bloqueante` si `tipo ∈ {SKILL_*}` · `advisory` si `tipo ∈ {PROMPT_CANONICO,
DEGRADAR}`. Cambiar qué dimensiones son bloqueantes es **CAMBIO**, no
calibración de config (v5 §3).

## 6. C12/C13 — escalado Advisory→Bloqueante

Solo si el grupo supera `n_adv_escalar` (100 nodos) **o** el `surprise_rate`
sale de banda: intervalo **Beta/Wilson** (no normalidad), `n_min_baseline=50`,
baseline rodante de 4 semanas con **`baseline_version`** registrada en cada
decisión. Sin baseline, el escalado no es reproducible. **C12 y C13 escalan
por separado**, cada una con su propio `baseline_version` (v6 corrección 5).

## 7. Parámetros del dominio prc

- `domain: prc` — cabecera obligatoria de toda propuesta de proceso.
- `pointer_enforcement_strict: true` — IDs canónicos exclusivos en
  dependencias/entradas/salidas (P-PRC-xx, PRM-, SKL-, BZ-, E-n, S-nn, P0x)
  contra el Índice Maestro; ID inexistente o texto descriptivo duplicado →
  FAIL.
- `snapshot_hash_validation: true` — toda modificación de los 14 procesos del
  snapshot v1 exige hash global JCS y versión nueva con traza; reescritura sin
  versión → RECHAZADO.
- **Matriz P29 binaria con BYPASS:** ¿recurrente ∨ multi-agente ∨ toca
  canónicos? Sí → ficha obligatoria · No → **BYPASS automático** (exención
  registrada, muestreo 10 % auditado, sin fricción).

## 8. Reglas de gobierno del sub-perfil

- El Crítico **no recalcula estadística**: Wilson la consume como evidencia.
- Cada dimensión es falsable con el bundle (n, w, replay_ids, hashes).
- Las `suggested_dimensions` siguen siendo **GUÍA NO VINCULANTE** para el
  triage (regla C1 CAMBIO-10 del config): la selección de `active_dimensions`
  es del autor; la composición/severidades de esta guía rigen el veredicto del
  perfil `ops.cosecha`.
- Umbrales en rango aprobado = config firmada; cambiar bloqueantes = CAMBIO.

## 9. Trazabilidad

- Propuesta: `docs/propuestas/PROP-COSECHA-001.md`.
- Config normativo: `04_critic.config.yaml → cosecha_prc` (slots C01–C13).
- Tests: `tests/test_subprofile_cosecha.py` (13).
- Freeze: `scripts/verify_freeze.py` (v3.5.0 + presencia del sub-perfil).

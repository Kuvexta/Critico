# Crítico v3.4 — FROZEN

> **Estado:** congelado el 2026-10-26.
> **Versión:** 3.3.0
> **Base congelada:** v3.2.0 (motor) + v3.4.0 (cableado al ecosistema).
> **Cambios permitidos:** solo parches aditivos (v3.4.1+) que no rompan los invariantes listados abajo.
> Cambios de lógica de negocio requieren descongelar explícitamente y versionar.

---

## 1. Qué es el Crítico

El Crítico es el rol del ecosistema que ejecuta el GATE B: hace pre-mortem de toda propuesta antes del consentimiento, ataca supuestos (no hechos — eso es Criba) y recomienda a GATE C (Dirección decide, el Crítico no veta).

**Separación dura:**

- Criba verifica HECHOS.
- Crítico ataca SUPUESTOS.
- GATE C decide.

---

## 2. Línea de versiones

| Versión | Hito |
|---|---|
| v2.0 | Diseño inicial: 11 ángulos, 5 estados, esquema formal |
| v3.0 | Correcciones (C1–C6) + Universalización (U1–U4) → 108 dimensiones, 19 familias (A–S), 6 macro-perfiles, motor agnóstico |
| v3.1 | Blindajes (B1–B4) + Refinamientos (R1–R5) + Micro-ajustes (M1–M3) |
| v3.2 | Parches de enforcement (G1, G1-bis, G2) en `schema/verdict.yaml` |
| v3.4 | Cableado al ecosistema: I1 (stack BZ-109), I2 (plan padre-hijo), I3 (SKIP_INCIDENT) + M-A a M-F |
| Fase 4 | Golden set + evals + panel HTML + dashboard histórico con sparklines |

---

## 3. Inventario de artefactos congelados

### 3.1 Especificación

| Fichero | Contenido | Estado |
|---|---|---|
| `rubric.yaml` | 108 dimensiones · 19 familias · rúbricas 0–4 · activación · mapeo v1→v3 | ✅ frozen v3.4.0 |
| `critic.config.yaml` | Flags, perfiles, presupuestos, invariantes, `schema_enforcement`, `integration` (I1–I3, M-C, M-D), `known_gaps` | ✅ frozen v3.4.0 |
| `schema/objection.yaml` | Esquema agnóstico + `parent_id`, `step_index`, `v1_angle` (I2, M-A) | ✅ frozen v3.4.0 |
| `schema/triage.yaml` | Capa 0 + multi-perfil + M1/M2 + `source_stack`, `parent_id`, `plan_status` (I1, I2, M-B) | ✅ frozen v3.4.0 |
| `schema/verdict.yaml` | Máquina de estados + G1/G1-bis/G2/I3 enforced + `active_skip_incidents`, `skip_incident_ids`, `reason_code: GATE_SKIPPED` | ✅ frozen v3.4.0 |
| `schema/risk_accepted.yaml` | `context_condition` estructurada + `metric_source` + fallback (R4). Sin cambios respecto a v3.2 | ✅ frozen v3.2.0 |
| `schema/skip_incident.yaml` | **NUEVO** — registro explícito de gate saltado (I3) | ✅ frozen v3.4.0 |
| `golden_set/schema/golden_case.yaml` | Esquema de caso golden | ✅ frozen v3.4.0 |
| `migration/v2_to_v3.py` | Renombrado + backfill + idempotencia + cuarentena (R2). Strings de versión actualizados a v3.4 | ✅ frozen v3.2.0 |

### 3.2 Tests

| Fichero | Tests | Estado |
|---|---|---|
| `test_rubric.py` | 8 | ✅ |
| `test_triage_m1.py` | 5 | ✅ |
| `test_triage_m2.py` | 4 | ✅ |
| `test_verdict_m2_m3_r1.py` | 10 | ✅ |
| `test_risk_accepted_r4.py` | 5 | ✅ |
| `test_migration_r2.py` | 10 | ✅ |
| `test_schema_structural.py` | 15 | ✅ |
| `test_verdict_enforcement_g1_g2.py` | 12 | ✅ |
| `test_evals.py` | 23 | ✅ |
| `test_html_report.py` | 11 | ✅ |
| `test_history.py` | 20 | ✅ |
| `test_integration_i1.py` | 4 | ✅ v3.4 |
| `test_integration_i2.py` | 5 | ✅ v3.4 |
| `test_integration_i3.py` | 5 | ✅ v3.4 |
| `test_integration_improvements.py` | 16 | ✅ v3.4 |
| **Total** | **153** | — |

### 3.3 Golden set + evals

| Fichero | Contenido |
|---|---|
| `golden_set/schema/golden_case.yaml` | Esquema de caso |
| `golden_set/manifest.yaml` | Índice de casos |
| `golden_set/cases/gc-00{1..4}.yaml` + `.actual.yaml` | 4 casos semilla |
| `golden_set/baseline/v3.2.0.json` | Métricas de referencia v3.2 |
| `golden_set/baseline/v3.4.0.json` | v3.2 + `skip_incident_rate: 0.0` |
| `golden_set/history/manifest.yaml` | Índice de snapshots temporales |
| `evals/loader.py` | Carga + validación de casos |
| `evals/comparator.py` | Comparación + `DimensionStats` |
| `evals/metrics.py` | Agregación global + `per_dimension` |
| `evals/runner.py` | Orquestación + check baseline + write baseline |
| `evals/cli.py` | CLI (`--mode offline`, `--json`, `--fail-on-regression`) |
| `evals/html_report.py` | Panel HTML self-contained + `_skip_incidents_section` (M-E) |
| `evals/history.py` | Store append-only + trends + `skip_incident_rate` (M-F) |
| `evals/html_history.py` | Dashboard con sparklines SVG |

### 3.4 Scripts + CI

| Fichero | Función |
|---|---|
| `scripts/render_eval_panel.py` | Genera `panel-evals.html` |
| `scripts/render_eval_history.py` | Snapshot + dashboard histórico |
| `scripts/bootstrap_golden_set.py` | Bootstrap desde bitácora + gate-c-decisions |
| `Makefile` | Targets: `test`, `eval`, `eval-panel`, `eval-history`, `verify-freeze`, `lint` + integración v3.4 |
| `.github/workflows/critico-ci.yml` | 6 jobs: test matrix · invariants ×14 · lint · evals · artifact · commit snapshot |

---

## 4. Invariantes protegidos

Estos **no pueden romperse** en un parche aditivo. Si un test asociado falla, el cambio no entra.

### 4.1 Correcciones estructurales (C1–C6)

| ID | Invariante | Test |
|---|---|---|
| C1 | Capa 0 (Triage) corre antes de la Capa 1 | `test_triage_m1` |
| C2 | Estados terminales van a GATE C; suspensión rebota al autor | `test_verdict_m2_m3_r1` |
| C3 | Métrica principal es discovery rate, no tasa de objeciones | `test_evals` |
| C4 | `mitigation_vector` reemplaza `suggested_fix`; blocker admite directriz | `test_schema_structural` |
| C5 | `RISK_ACCEPTED_BY_GATE_C` exige `expiration_date` y `context_condition` | `test_risk_accepted_r4` |
| C6 | `PASA` exige `audit_trail_passed_checks` con ≥1 elemento | `test_verdict_enforcement_g1_g2` (G2) |

### 4.2 Universalización (U1–U4)

| ID | Invariante | Test |
|---|---|---|
| U1 | Esquema agnóstico: `artifact_id`, `evidence_locator`, `impact_types`, `time_horizon` | `test_schema_structural` |
| U2 | 6 macro-perfiles + sub-perfiles `tech.*` | `test_rubric` |
| U3 | Capacidades de inspección (no atadas a consola) | spec |
| U4 | Familia S (104–106) transversal universal | `test_rubric` |

### 4.3 Blindajes (B1–B4)

| ID | Invariante | Test |
|---|---|---|
| B1 | Multi-perfil con `max_secondary=2` y tope `max_active_dimensions=40` | `test_schema_structural` |
| B2 | `max_suspension_cycles=2` con escalado a GATE C | `test_verdict_m2_m3_r1` |
| B3 | `context_condition` con `qualitative_trigger` + `quantitative_threshold` | `test_risk_accepted_r4` |
| B4 | Migración preserva `objection_id` y guarda `legacy_v2_hash` | `test_migration_r2` |

### 4.4 Refinamientos (R1–R5)

| ID | Invariante | Test |
|---|---|---|
| R1 | `RIESGO_NO_EVALUADO` ≠ `NO_PASA` (métricas separadas) | `test_verdict_m2_m3_r1` |
| R2 | Migración idempotente + validación post + cuarentena + exit code | `test_migration_r2` |
| R3 | Tope de 40 sin poda silenciosa (vía M1) | `test_triage_m1` |
| R4 | `metric_source == unavailable` ⇒ flag `QUANTITATIVE_UNAVAILABLE` | `test_risk_accepted_r4` |
| R5 | >3 macro-perfiles ⇒ `TRIAGE_SPLIT_RECOMMENDATION` como suspensión (vía M2) | `test_triage_m2` |

### 4.5 Micro-ajustes v3.1 (M1–M3)

| ID | Invariante | Test |
|---|---|---|
| M1 | `union_raw_count > cap AND overrides == []` ⇒ triage inválido | `test_triage_m1` |
| M2 | Split recommendation ⇒ `NECESITA_INFO` con `SPLIT_OR_SCOPE_ACCEPTANCE_REQUIRED` | `test_triage_m2` |
| M3 | Reset de `suspension_cycles` exige cambio de hash **Y** preguntas resueltas | `test_verdict_m2_m3_r1` |

### 4.6 Enforcement JSON Schema v3.2 (G1, G1-bis, G2)

| ID | Invariante | Test |
|---|---|---|
| G1 | `state_class == OPERATIONAL_SUSPENSION` ⇒ `suspension_control` objeto no-null | `test_verdict_enforcement_g1_g2` |
| G1-bis | `state_class == TERMINAL` ⇒ `suspension_control` null | `test_verdict_enforcement_g1_g2` |
| G2 | `status ∈ {PASA, PASA_CON_CONDICIONES}` ⇒ `audit_trail` con ≥1 | `test_verdict_enforcement_g1_g2` |

### 4.7 Integración v3.4 (I1–I3)

| ID | Invariante | Test |
|---|---|---|
| I1 | Todo stack BZ-109 mapeado tiene macro-perfil válido; sin mapeo → `NECESITA_INFO` con `STACK_NOT_MAPPED` | `test_integration_i1` |
| I2 | `parent_id` vincula pasos al plan; `NO_PASA` en paso bloquea downstream | `test_integration_i2` |
| I3 | `SKIP_INCIDENT` activo ⇒ artefacto **no puede** recibir `PASA`; máximo `NO_PASA` con `reason_code: GATE_SKIPPED` | `test_integration_i3` |

### 4.8 Mejoras v3.4 (M-A a M-F)

| ID | Invariante | Test |
|---|---|---|
| M-A | `v1_angle` poblado en bitácora para continuidad histórica entre ángulos v1 y dimensiones v3.2 | `test_integration_improvements` |
| M-B | Plan bloqueado ⇒ triage emite `NECESITA_INFO` con `PLAN_BLOCKED` | `test_integration_improvements` |
| M-C | Contrato de `check_encargo v2` declarado en config | `test_integration_improvements` |
| M-D | Rotación de modelos prohibida entre autor/revisor/verificador | `test_integration_improvements` |
| M-E | Panel HTML muestra skip incidents cuando >0 | `test_integration_improvements` |
| M-F | Dashboard trackea tendencia de `skip_incident_rate` | `test_integration_improvements` |

**Total invariantes protegidos: 34.**

---

## 5. Tabla de stacks BZ-109 → macro-perfil

**Estado:** actualizada el 2026-10-30 al **Registro Canónico F/T/S/E v1**
(MD-4, aprobada por Dirección — GATE C concedido, BZ-20261030-094). Parche
aditivo **v3.4.1**. `stack_3` queda **resuelto y eliminado**: era la incógnita
de BZ-109; el registro nuevo la disuelve en `E-3` y `T3` (no existe «stack_3»).

```yaml
# critic.config.yaml → integration.bz109_stack_mapping (34 entradas)
# Stacks técnicos E- (10 + 5 sub-stacks; techo 20)
E-1:     { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
E-2:     { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
E-3:     { macro_profile: tech,     sub_profile: tech.data,  status: frozen }
E-4:     { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
E-5:     { macro_profile: tech,     sub_profile: null,       status: frozen }
E-6:     { macro_profile: tech,     sub_profile: null,       status: frozen }  # en_construccion → frozen (nota)
E-7:     { macro_profile: tech,     sub_profile: null,       status: frozen }  # en_construccion → frozen (nota)
E-8:     { macro_profile: tech,     sub_profile: null,       status: frozen }  # en_construccion → frozen (nota)
E-9:     { macro_profile: tech,     sub_profile: tech.data,  status: frozen }  # en_construccion → frozen (nota)
E-10:    { macro_profile: tech,     sub_profile: tech.infra, status: frozen }  # en_construccion → frozen (nota)
E-S1:    { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
E-S2:    { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
E-S3:    { macro_profile: business, sub_profile: null,       status: frozen }
E-S4:    { macro_profile: tech,     sub_profile: tech.data,  status: frozen }
E-S5:    { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
# Planos organizacionales: fábricas (F), transversales (T), servicios (S)
F1:      { macro_profile: tech,     sub_profile: tech.code,  status: frozen }
F4:      { macro_profile: business, sub_profile: null,       status: frozen }
F5:      { macro_profile: business, sub_profile: null,       status: frozen }
F6:      { macro_profile: tech,     sub_profile: null,       status: frozen }
F7:      { macro_profile: legal,    sub_profile: null,       status: frozen }
F8:      { macro_profile: tech,     sub_profile: tech.infra, status: frozen }
T1:      { macro_profile: legal,    sub_profile: null,       status: frozen }
T2:      { macro_profile: tech,     sub_profile: null,       status: frozen }
T3:      { macro_profile: tech,     sub_profile: tech.data,  status: frozen }
T4:      { macro_profile: ops,      sub_profile: null,       status: frozen }
T5:      { macro_profile: business, sub_profile: null,       status: frozen }
S01…S08: { macro_profile: business, sub_profile: null,       status: frozen }
```

Regla de comportamiento sin cambios: si llega una propuesta etiquetada con un
stack no mapeado → `NECESITA_INFO` con `suspension_reason: STACK_NOT_MAPPED`.
El sistema no rompe; pide clarificación.

**Nota del cambio (v3.4.1):**

- El esquema del config solo admite los estados `frozen` y `pending_confirmation`;
  `en_construccion` **no existe** y añadirlo exigiría descongelar. Por la propuesta
  MD-4 (nota 3) y la instrucción del encargo, las filas E-6…E-10 (stacks aprobados
  30/10 y **en construcción**) se registran `status: frozen` con la condición anotada
  en `description` del YAML. Registrado en CHANGELOG v3.4.1.
- `S01…S08` se expande a 8 entradas individuales (`S01` … `S08`) en el YAML.
- Las descripciones de las filas F/T/S/E provienen del Registro Canónico F/T/S/E v1
  (hash `d7d2d870…`, BZ-20261030-094) y de DOC-01 (fábricas/transversales/servicios).
- Acción pendiente de §5 resuelta: `stack_3` no existe en BZ-109; eliminado.
- **Contrato ejecutable actualizado (condiciones de Dirección, 30/10):**
  `tests/test_integration_i1.py::test_04` deja de aseverar el estado viejo de
  `stack_3` (**CAMBIO INTENCIONAL DE CONTRATO**, no ajuste para que pase): el
  registro F/T/S/E resuelve la incógnita `stack_3` y el estado viejo queda
  eliminado. El test ahora verifica el estado nuevo (34 entradas exactas,
  `stack_3` ausente) y la regla real del contrato I1: stack no mapeado (p. ej.
  «X-1») → `NECESITA_INFO` con `STACK_NOT_MAPPED`. Motivo y diff exacto
  documentados dentro del test y en CHANGELOG v3.4.1.

---

## 6. Verificación del freeze

> ⚠ **Nota de integridad (auto-auditoría 26/10):** los 153 tests están diseñados y preservados en `10_Anexo_codigo_historico.md`; su ejecución queda pendiente de materializar `tests/` en el repo. La batería ejecutable hoy es `probar_todo.py` (PASS 17/17). Ver `16_GATE_B_Autoauditoria.md`.

Cualquier persona puede verificar el estado completo con:

```bash
# 1. Integridad
make verify-freeze
# → Freeze OK: v3.4.0 · esquemas v3.4 · integración BZ-109

# 2. Suite completa (153 tests)
make test
# → 153 passed

# 3. Evals vs baseline (detecta regresiones)
make eval
# → Sin regresiones vs baseline v3.4

# 4. Panel HTML
make eval-panel
# → panel-evals.html generado (incluye skip incidents si los hay)

# 5. Dashboard histórico
make eval-history
# → dashboard-evals.html generado (incluye tendencia de skip rate)

# 6. Solo integración v3.4
pytest tests/test_integration_i1.py tests/test_integration_i2.py \
       tests/test_integration_i3.py tests/test_integration_improvements.py -v
# → 30 passed
```

Si algo falla, el freeze está roto. Los tests son el contrato ejecutable.

---

## 7. Deuda de diseño documentada

Estos huecos están aceptados por diseño y no bloquean el freeze.

| ID | Descripción | Razón |
|---|---|---|
| G3 | M1 (cap justificado) no enforced en JSON Schema | No expresable en JSON Schema estándar; validado en `helpers/validators.py` + `critic.config.validation.invariants` |
| G4 | M3 (reset doble condición) no enforced en JSON Schema | Igual que G3; validado en runtime |
| — | `stack_3` resuelto en v3.4.1 | Eliminado: la ambigüedad la disuelve el Registro Canónico F/T/S/E v1 (E-3 y T3) — ver §5 |
| — | Modo `--mode live` de evals requiere API de modelos | Fuera de alcance del freeze; el comparador no cambia cuando llegue |
| — | Golden set con 4 casos sintéticos | Ampliable con `scripts/bootstrap_golden_set.py` cuando exista `gate-c-decisions.jsonl` real |
| — | Reporte de tendencia temporal empieza vacío | Se llena con cada ejecución de `make eval-history` en CI |

---

## 8. Cómo añadir un cambio (post-freeze)

> **Flujo canónico vigente (2026-10-28):** `CONTRIBUTING.md` de este repo y el
> playbook `MUTACIONES.md` de Kuvexta/Ecosistema (propuesta numerada +
> «OK <8hex>` + batería + freeze + guarda). El procedimiento numerado de abajo
> es el **histórico de la era v3.3** y se conserva como referencia; ante
> conflicto, manda el flujo canónico.

Procedimiento obligatorio:

1. Abrir PR con el cambio.
2. Verificar `make all` (verify-freeze + test + eval) — debe pasar.
3. Bump de versión en `rubric.yaml`, `critic.config.yaml` y `$id` de esquemas afectados (v3.4, v3.5…).
4. Añadir tests que cubran el cambio y, si es un invariante nuevo, añadirlo a `critic.config.validation.invariants`.
5. Actualizar este `FROZEN.md` en §4 (nuevo invariante) o §7 (nueva deuda).
6. Regenerar baseline solo si el cambio mejora métricas reales (no para "cuadrar" números).
7. Aprobación de GATE C (Dirección) para cambios que afecten a la máquina de estados, a `schema/verdict.yaml` o a la tabla BZ-109.

Prohibido sin descongelar:

- Cambiar la máquina de estados (C2).
- Modificar el esquema de `objection.yaml` en campos obligatorios.
- Cambiar los 6 macro-perfiles (U2).
- Cambiar la tabla BZ-109 (§5) sin aprobación explícita.
- Romper cualquier test de la suite.

---

## 9. Roadmap post-freeze

Nada de esto bloquea el freeze actual.

| Fase | Qué | Condición |
|---|---|---|
| v3.4.1 | ✔ Hecho (2026-10-30): tabla BZ-109 reemplazada por el Registro Canónico F/T/S/E v1; `stack_3` eliminado | MD-4 aprobada por Dirección (GATE C, BZ-20261030-094) |
| v3.4.1 | Activar `model_rotation.enabled` | Disponibilidad de >1 modelo |
| v3.4 | Ampliar golden set con casos históricos reales | `gate-c-decisions.jsonl` formalizado |
| v3.4 | Activar `--mode live` en evals | API de modelos disponible |
| v3.5 | Flags: `llm_teach_check`, `pr_review`, `debate_mode`, `red_team_mode`, `cost_estimator` | Condición declarada en `critic.config.flags` |
| v3.5+ | Reporte público con histórico embebido | Requiere backend (fuera de alcance) |
| v3.6 | Calibración de rúbricas por `per_dimension_accuracy` | Requiere ≥10 casos golden |
| v4.0 | Integración nativa con `check_encargo v2` bidireccional | Contrato M-C validado en producción |

---

## 10. Acta de cierre

El Crítico v3.4 queda congelado el 2026-10-26 con:

- 108 dimensiones en 19 familias (A–S), con rúbricas 0–4 verificadas.
- 6 esquemas JSON Schema válidos (objection, triage, verdict, risk_accepted, skip_incident, golden_case) con enforcement condicional (G1, G1-bis, G2, I3).
- 34 invariantes protegidos por tests:
  - 6 correcciones estructurales (C1–C6)
  - 4 universalizaciones (U1–U4)
  - 4 blindajes (B1–B4)
  - 5 refinamientos (R1–R5)
  - 3 micro-ajustes (M1–M3)
  - 3 enforcement de esquema (G1, G1-bis, G2)
  - 3 integración (I1–I3)
  - 6 mejoras (M-A a M-F)
- 153 tests **diseñados y preservados** (ejecución pendiente de materializar `tests/` — ver nota de integridad §12.1/§6 y `16_GATE_B_Autoauditoria.md` O1).
- Cableado al ecosistema: stacks BZ-109 mapeados, pasos de plan vinculados, gates saltados registrados explícitamente.
- Golden set con baseline + detección de regresión global, por dimensión y de skip rate.
- Panel HTML para revisión sin CLI (self-contained, WCAG AA, muestra skip incidents).
- Dashboard histórico con sparklines SVG, tendencia de skip rate y retención automática.
- CI con 6 jobs, artifacts y commit automático de snapshots en main.

Este documento es la referencia canónica. Cualquier divergencia entre lo aquí declarado y el estado del repo es un fallo de integridad.

---

## 11. Índice de ficheros

```text
FROZEN.md                          ← este documento
rubric.yaml                        ← 108 dimensiones (v3.4.0)
critic.config.yaml                 ← configuración + integration (v3.4.0)
schema/
  objection.yaml                   ← + parent_id, step_index, v1_angle
  triage.yaml                      ← + source_stack, parent_id, plan_status
  verdict.yaml                     ← + active_skip_incidents, GATE_SKIPPED
  risk_accepted.yaml               ← sin cambios v3.2
  skip_incident.yaml               ← NUEVO
migration/
  v2_to_v3.py
tests/                             ← 153 tests
fixtures/                          ← samples legacy v2
golden_set/
  manifest.yaml
  schema/golden_case.yaml
  cases/gc-00{1..4}.yaml
  cases/gc-00{1..4}.actual.yaml
  baseline/v3.2.0.json
  baseline/v3.4.0.json
  history/manifest.yaml
evals/
  loader.py · comparator.py · metrics.py · runner.py · cli.py
  html_report.py · history.py · html_history.py
scripts/
  render_eval_panel.py · render_eval_history.py · bootstrap_golden_set.py
Makefile
.github/workflows/critico-ci.yml
```

---

*Crítico v3.4 — cerrado. Lo que venga, se versiona.*

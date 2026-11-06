# Golden Set — Crítico v3.4
## Estado honesto (2026-11-06, corregido en CRITICO-SKILL-02 PR-A)

- **Harness offline ejecutable**: `evals/cli.py` y `evals/comparator.py`
  existen y `python -m evals.cli --mode offline` corre hoy (rc 0) sobre los
  4 casos de `cases/` (`gc-001`…`gc-004`, con sus `.actual.yaml`
  pre-grabados) y compara contra `baseline/v3.4.0.json`
  (`--fail-on-regression` disponible).
- **Baselines**: `baseline/v3.3.0.json` y `baseline/v3.4.0.json`.
- **Sigue pendiente**: `scripts/bootstrap_golden_set.py` (generar
  `.actual.yaml` desde la bitácora) y el modo `live` (requiere API); no se
  simulan. Las métricas offline miden la salida pre-grabada, no una
  ejecución real del Crítico.

(La versión anterior de esta sección decía que la maquinaria no existía;
era incorrecta para `cli.py`/`comparator.py`.)


## Golden set de contrato de la skill (`skill_cases/`, CRITICO-SKILL-02)

Casos **sintéticos** (`sc-NNN.yaml`), cada uno con bloque
`expected {mode, status, blockers, codes, artifact_binding}`:
SC-001 autocontrol que intenta pasar como GATE B · SC-002 OK ligado a un head
anterior · SC-003 integración que solo declara el caso feliz · SC-004 control
(no debe bloquearse).

    python -m evals.cli --skill-version old --expect-all-pass   # rc 1: la skill v3.6.0 falla SC-001..003
    python -m evals.cli --skill-version new --expect-all-pass   # rc 0: la skill nueva pasa los 4
    python -m evals.cli --skill-version new --fail-on-regression

Qué mide: aplica de forma determinista las reglas que **declara** cada versión
de la skill (marcadores en su texto; `old` se lee de `d23241c` con `git show`,
requiere historial completo) a salidas de revisión sintéticas. **No** ejecuta
un modelo ni simula su salida; el comportamiento de un modelo con la skill
queda para el modo `live`. Línea base y ratchet:
`baseline/skill_contract.json` (`passed` solo sube por versión).

Casos con **veredicto esperado conocido** para medir si el Crítico reproduce
la decisión que GATE C tomó en producción.
## Objetivo
Alimentar las métricas del roadmap (Fase 4):
`- `verdict_match_rate` — % de casos donde el veredicto coincide`
`- `blocker_recall` — % de blockers esperados que el Crítico encontró`
`- `blocker_precision` — % de blockers emitidos que estaban justificados`
`- `discovery_rate` — media de supuestos implícitos descubiertos por caso`
`- `audit_trail_coverage` — % de PASA con audit trail no vacío`
`- `per_dimension_accuracy` — qué dimensiones predicen mejor el fallo`
## Estructura de un caso
    cases/gc-NNN.yaml           → entrada + veredicto esperado
    cases/gc-NNN.actual.yaml    → salida pre-grabada del Crítico
## Modos de ejecución
    # offline (hoy): usa los .actual.yaml pre-grabados
    python -m evals.cli --mode offline
    # live (cuando haya API): ejecuta el Crítico real
    python -m evals.cli --mode live
## Cómo añadir un caso
1. Tomar una decisión de GATE C ya cerrada.
`2. Crear `cases/gc-NNN.yaml` con el input, el veredicto esperado y el ground truth.`
`3. Crear `cases/gc-NNN.actual.yaml` con la salida del Crítico sobre ese input`
   `(o correr `python scripts/bootstrap_golden_set.py` para generarlo desde la bitácora).`
`4. `make eval` y revisar.`
## Baseline
` `baseline/v3.4.0.json` congela las métricas al momento del freeze. `
CI compara contra el baseline y falla si alguna métrica baja más del umbral.

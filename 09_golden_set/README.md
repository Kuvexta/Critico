# Golden Set — Crítico v3.4
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

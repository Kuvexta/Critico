# Guía de esquemas — Español
Autor: KUVEXTA GROUP. Revisada el 2026-10-27 contra los archivos intactos de `05_schema/`.
Los YAML contienen JSON Schema y son los contratos normativos. Esta guía explica su uso sin renombrar campos ni traducir valores de máquina. Las listas de campos obligatorios se extraen de cada esquema. Los opcionales también se validan cuando aparecen. Omitir un campo no equivale a incluir `null`: úsalo solo si el esquema lo admite.

| Esquema | Finalidad |
| --- | --- |
| objection | Objeción falsable: afirmación, mejor defensa, supuestos, evidencia, contrafactual, falsación y mitigación |
| triage | Perfiles, dimensiones activas/podadas, excepciones, presupuesto y preguntas anteriores |
| verdict | Decisión o suspensión operativa, motivos, trazabilidad y métricas |
| outcome | Observaciones posteriores, fallos previstos/no previstos e intervenciones |
| risk_accepted | Aceptación explícita, responsable, justificación, condiciones y caducidad |
| skip_incident | Evidencia de un gate omitido y su resolución |
| pattern | Patrón reutilizable derivado de observaciones repetidas |
| golden_case | Artefacto de referencia, triage, comportamiento esperado, verdad de referencia y metadatos |

## Reglas además de la estructura
Usa `critico_cli.py validar` (alias `critic_cli.py validate`) y `verificar`/`verify` para las invariantes de ejecución. Leer YAML no equivale a validarlo. El modo borrador no acredita un veredicto final. Las plantillas son ejemplos iniciales, no evidencia.

- `artifact_id`, `verdict_id`, `objection_id` e IDs de dimensión enlazan registros: conserva sintaxis e identidad. `provenance.artifact_hash` identifica contenido mediante SHA-256; coincidencia no demuestra veracidad.
- `status`, `state_class`, `reason_code` y códigos I3/M3/G5 son contratos de máquina. PASA/NO_PASA y los demás enums se conservan en ambos idiomas.
- Un reset M3 exige preguntas anteriores resueltas, referencia concreta `summary_metrics.reset_of_suspension`, registro histórico OPERATIONAL_SUSPENSION válido y sin ambigüedad, su `artifact_hash_at_suspension` y un hash diferente calculado del artefacto real. Una afirmación manual no basta.
- `evidence_detail` registra fuente, fecha de acceso y tipo (`hecho`, `inferencia`, `hipotesis`). HASH_VERIFICADO significa coincidencia de contenido; NO_VERIFICADO(sin_hash|remoto|inaccesible) no acredita nada. El desacuerdo de hash rechaza. No se traducen entradas del usuario ni se consultan referencias remotas para localizar mensajes.
- `materialized` mantiene `si`, `no`, `parcial`, `desconocido`. Escribe `"no"` entre comillas YAML. `mitigacion_aplicada` y `propuesta_cancelada` informan intervenciones separadas; null significa no informada, no falso. No se infiere causalidad.
- La tasa de intervención cuenta decisiones observadas por verdict_id único, como máximo una vez cada una. Las decisiones solo desconocidas quedan fuera del denominador. La intervención no informada se contabiliza aparte en todas las decisiones.
- `seguimiento.completo: false` y `omitidos` muestran seguimiento parcial; omitir no es éxito. G5 exige resultados de objeciones o fallos no previstos; un outcome con solo fallos no previstos puede ser válido.
- El riesgo aceptado tiene caducidad y condiciones; aceptarlo no elimina la objeción. Un gate omitido no puede convertirse en PASA al cambiar el idioma.
- Fechas, severidades, horizontes, perfiles y arrays obligatorios conservan su semántica. Consulta los esquemas anidados para límites, miembros obligatorios, enums y condiciones cruzadas.

## Inventario de contratos

### golden_case

https://critico/v3.4/golden/golden_case.yaml

Obligatorios: `case_id`, `artifact`, `triage`, `expected`, `ground_truth`, `metadata`.

Todos los campos del primer nivel: `case_id`, `artifact`, `triage`, `expected`, `ground_truth`, `metadata`.

### objection

https://critico/v3.4/schema/objection.yaml

Obligatorios: `objection_id`, `gate`, `artifact_id`, `domain_profile`, `timestamp`, `dimension`, `severity`, `claim`, `steelman`, `assumptions`, `evidence_locator`, `counterfactual`, `falsification`, `mitigation_vector`, `mitigation_type`, `verification_mechanism`, `blast_radius`, `time_horizon`, `confidence`, `provenance`.

Todos los campos del primer nivel: `objection_id`, `gate`, `artifact_id`, `domain_profile`, `timestamp`, `dimension`, `severity`, `claim`, `steelman`, `assumptions`, `evidence_locator`, `counterfactual`, `falsification`, `mitigation_vector`, `mitigation_type`, `verification_mechanism`, `blast_radius`, `time_horizon`, `confidence`, `parent_id`, `step_index`, `v1_angle`, `evidence_detail`, `contradictory_evidence`, `unverified_info`, `provenance`.

### outcome

https://critico/v3.4/schema/outcome.yaml

Obligatorios: `outcome_id`, `verdict_id`, `artifact_id`, `horizon`, `observed_at`, `provenance`.

Todos los campos del primer nivel: `outcome_id`, `verdict_id`, `artifact_id`, `horizon`, `observed_at`, `objection_outcomes`, `unpredicted_failures`, `calibration_sample`, `seguimiento`, `rework`, `provenance`.

### pattern

https://critico/v3.4/schema/pattern.yaml

Obligatorios: `pattern_id`, `family`, `dimensions`, `description`, `severity`, `evidence`, `count`.

Todos los campos del primer nivel: `pattern_id`, `family`, `dimensions`, `keywords`, `profiles`, `severity`, `description`, `steelman`, `evidence`, `count`, `confidence_gain`, `provenance`.

### risk_accepted

https://critico/v3.2/schema/risk_accepted.yaml

Obligatorios: `objection_id`, `status`, `accepted_by`, `date`, `expiration_date`, `context_condition`, `rationale`.

Todos los campos del primer nivel: `objection_id`, `status`, `accepted_by`, `date`, `expiration_date`, `rationale`, `context_condition`, `flag`, `provenance`.

### skip_incident

https://critico/v3.4/schema/skip_incident.yaml

Obligatorios: `incident_id`, `artifact_id`, `expected_gate`, `detected_by`, `detected_at`, `severity`, `policy_ref`.

Todos los campos del primer nivel: `incident_id`, `artifact_id`, `expected_gate`, `detected_by`, `detected_at`, `severity`, `policy_ref`, `evidence`, `resolution`.

### triage

https://critico/v3.4/schema/triage.yaml

Obligatorios: `triage_id`, `artifact_id`, `timestamp`, `profiles`, `dimensions_summary`, `active_dimensions`, `pruned_families`, `triage_overrides`, `config_ref`.

Todos los campos del primer nivel: `triage_id`, `artifact_id`, `timestamp`, `source_stack`, `parent_id`, `profiles`, `dimensions_summary`, `active_dimensions`, `pruned_families`, `triage_overrides`, `triage_split_recommendation`, `plan_status`, `previous_suspension_questions_resolved`, `config_ref`.

### verdict

https://critico/v3.4/schema/verdict.yaml

Obligatorios: `verdict_id`, `artifact_id`, `gate`, `timestamp`, `state_class`, `status`.

Todos los campos del primer nivel: `verdict_id`, `artifact_id`, `gate`, `timestamp`, `state_class`, `status`, `reason_code`, `suspension_control`, `audit_trail_passed_checks`, `summary_metrics`.

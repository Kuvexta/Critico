# Schema guide — English
Author: KUVEXTA GROUP. Reviewed 2026-10-27 against the unchanged files in `05_schema/`.
The YAML files contain JSON Schema. They are the authoritative contracts; this guide explains them, without renaming fields or translating wire values. Each required-field list below is extracted from the actual schema. Optional fields are still constrained when present. Missing and explicit `null` are different: do not add null unless the schema permits it.

| Schema | Purpose |
| --- | --- |
| objection | A falsifiable criticism: claim, strongest case, assumptions, evidence, counterfactual, falsification procedure and mitigation |
| triage | Profile selection and the active/pruned dimension set, overrides, budget and prior-question state |
| verdict | Decision or operational suspension, reasons, audit trail and metrics |
| outcome | Observations following a decision, predicted/unpredicted failures and interventions |
| risk_accepted | Explicit acceptance by a named party, rationale, conditions and expiry |
| skip_incident | Evidence that a required gate was skipped and its resolution |
| pattern | Reusable pattern derived from repeated observations |
| golden_case | Reference artifact, triage, expected behavior, ground truth and metadata |

## Rules beyond shape validation
Use `critic_cli.py validate` (legacy `critico_cli.py validar`) and `verify`/`verificar` for runtime invariants; parsing YAML alone is not validation. Draft mode does not establish a final verdict. Templates are starting examples, not evidence.

- `artifact_id`, `verdict_id`, `objection_id` and dimension IDs link records. Preserve their syntax and identity. `provenance.artifact_hash` is a SHA-256 content identifier; hash agreement does not prove truth.
- `status`, `state_class`, `reason_code` and codes such as I3/M3/G5 are machine contracts. Keep PASA/NO_PASA and all other declared enum values unchanged in either language.
- M3 reset needs resolved earlier questions, a concrete suspension reference (`summary_metrics.reset_of_suspension`), an unambiguous schema-valid historical OPERATIONAL_SUSPENSION record, its recorded `artifact_hash_at_suspension`, and a different hash calculated from the actual artifact. Manual assertions are insufficient.
- `evidence_detail` records source, access time and kind (`hecho`, `inferencia`, `hipotesis`). HASH_VERIFICADO means content matches; NO_VERIFICADO(sin_hash|remoto|inaccesible) is not proof. A hash disagreement rejects. User evidence and remote references are never translated or fetched for localization.
- `materialized` preserves `si`, `no`, `parcial`, `desconocido`. Quote YAML `"no"`. `mitigacion_aplicada` and `propuesta_cancelada` are separate intervention reports; null means not reported, not false. No automatic causal claim.
- Intervention rate counts unique observed verdict_id decisions, once each. Unknown-only decisions are outside its denominator. Unreported intervention information is counted separately across decisions.
- `seguimiento.completo: false` and `omitidos` expose partial tracking; an omission is not success. G5 requires objection outcomes or unpredicted failures; unpredicted-only outcomes can be valid.
- Accepted risk has expiry and context conditions; acceptance does not delete the objection. A skipped gate cannot become PASA merely by changing language.
- Date strings, severity, horizons, profile names and required arrays retain schema semantics. Consult the actual nested schema for bounds, required members, enums and cross-field constraints.

## Contract inventory

### golden_case

https://critico/v3.4/golden/golden_case.yaml

Required: `case_id`, `artifact`, `triage`, `expected`, `ground_truth`, `metadata`.

All top-level fields: `case_id`, `artifact`, `triage`, `expected`, `ground_truth`, `metadata`.

### objection

https://critico/v3.4/schema/objection.yaml

Required: `objection_id`, `gate`, `artifact_id`, `domain_profile`, `timestamp`, `dimension`, `severity`, `claim`, `steelman`, `assumptions`, `evidence_locator`, `counterfactual`, `falsification`, `mitigation_vector`, `mitigation_type`, `verification_mechanism`, `blast_radius`, `time_horizon`, `confidence`, `provenance`.

All top-level fields: `objection_id`, `gate`, `artifact_id`, `domain_profile`, `timestamp`, `dimension`, `severity`, `claim`, `steelman`, `assumptions`, `evidence_locator`, `counterfactual`, `falsification`, `mitigation_vector`, `mitigation_type`, `verification_mechanism`, `blast_radius`, `time_horizon`, `confidence`, `parent_id`, `step_index`, `v1_angle`, `evidence_detail`, `contradictory_evidence`, `unverified_info`, `provenance`.

### outcome

https://critico/v3.4/schema/outcome.yaml

Required: `outcome_id`, `verdict_id`, `artifact_id`, `horizon`, `observed_at`, `provenance`.

All top-level fields: `outcome_id`, `verdict_id`, `artifact_id`, `horizon`, `observed_at`, `objection_outcomes`, `unpredicted_failures`, `calibration_sample`, `seguimiento`, `rework`, `provenance`.

### pattern

https://critico/v3.4/schema/pattern.yaml

Required: `pattern_id`, `family`, `dimensions`, `description`, `severity`, `evidence`, `count`.

All top-level fields: `pattern_id`, `family`, `dimensions`, `keywords`, `profiles`, `severity`, `description`, `steelman`, `evidence`, `count`, `confidence_gain`, `provenance`.

### risk_accepted

https://critico/v3.2/schema/risk_accepted.yaml

Required: `objection_id`, `status`, `accepted_by`, `date`, `expiration_date`, `context_condition`, `rationale`.

All top-level fields: `objection_id`, `status`, `accepted_by`, `date`, `expiration_date`, `rationale`, `context_condition`, `flag`, `provenance`.

### skip_incident

https://critico/v3.4/schema/skip_incident.yaml

Required: `incident_id`, `artifact_id`, `expected_gate`, `detected_by`, `detected_at`, `severity`, `policy_ref`.

All top-level fields: `incident_id`, `artifact_id`, `expected_gate`, `detected_by`, `detected_at`, `severity`, `policy_ref`, `evidence`, `resolution`.

### triage

https://critico/v3.4/schema/triage.yaml

Required: `triage_id`, `artifact_id`, `timestamp`, `profiles`, `dimensions_summary`, `active_dimensions`, `pruned_families`, `triage_overrides`, `config_ref`.

All top-level fields: `triage_id`, `artifact_id`, `timestamp`, `source_stack`, `parent_id`, `profiles`, `dimensions_summary`, `active_dimensions`, `pruned_families`, `triage_overrides`, `triage_split_recommendation`, `plan_status`, `previous_suspension_questions_resolved`, `config_ref`.

### verdict

https://critico/v3.4/schema/verdict.yaml

Required: `verdict_id`, `artifact_id`, `gate`, `timestamp`, `state_class`, `status`.

All top-level fields: `verdict_id`, `artifact_id`, `gate`, `timestamp`, `state_class`, `status`, `reason_code`, `suspension_control`, `audit_trail_passed_checks`, `summary_metrics`.

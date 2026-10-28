# CHANGELOG — Critic (system, documents and folder)

[Spanish source](../../CHANGELOG.md). Translation dated 2026-10-27.

> Organized by date. System v3.3.0 frozen; manual document v1.0.0; universal design v1.1.0.

## 2026-10-27 — BILINGUE-CRITICO-01

- English internals with compatible Spanish aliases and keyword arguments; shared English entry points.
- Spanish/English message catalogues, language selection, localized help and HTML labels; protocol fields and decisions remain unchanged.
- Bilingual current documentation, manual, universal design and one manually invoked read-only skill.
- Translation source hashes and a separate delivery package. Consult RESULTS.json for final test results; this entry does not certify independent review.

## 2026-10-27 — AUTORIA-LICENCIAS-01

- Project author identified as KUVEXTA GROUP, without attributing third-party materials.
- Inactive catalogue: MIT, Apache-2.0, MPL-2.0, GPL-3.0-only, AGPL-3.0-only, CC BY and CC BY-SA 4.0; reference copies with URL, date and SHA-256.
- Inactive drafts for proprietary commercial, source-available and dual-licensing models.
- Inventory of dependency notices observed in the environment, without relicensing them.
- Prior LICENSE declaration preserved. Future license selection and application require a separate decision.
- New package with its own manifest; functional code and closure-v1 delivery preserved. Source: the license delivery's INFORME.md and inventories.

## 2026-10-26 — CIERRE-CRITICO-01 (local assisted version)

- Shared validation across CLI, initializer and metrics: operational dates, explicit drafts, bidirectional states, consistent counts and tracking.
- M3 rejects invalid history and ambiguous suspensions; compares the identified suspension with the computed current hash.
- Document-relative local evidence and inaccessible-source handling; HASH_VERIFICADO demonstrates integrity, not truth.
- Migration with mandatory actual validation, revalidated idempotence, preserved input and quarantine. Patterns accept a list or container.
- Suite distinguishes passed/failed/not verifiable checks, reports cleanup failures and uses owned temporary files. Adds a synthetic workflow and contract, migration and reporting regressions.
- Manual read-only skill and separation of method, policy, contracts and integration. Package with SHA-256 manifest, inventories, logs and coverage matrix.
- Isolated environment authorized by ENTORNO-CIERRE-01. Exact dependencies and results in the delivery; no installation or migration into the workspace.
- Earlier entries are project history. Their counts are not current results or independent ratification. Historical incidents remain pending human decision.

Closure source: code, closure-v1's RESULTADOS.json and associated logs dated 2026-10-26. Any subsequent result must identify its own source hashes.

## 2026-10-26 — Creation and consolidation

### System (v2.0 → v3.3.0)

- v2.0: 11 angles, initial design · v3.0: C1–C6 + U1–U4 (106 dimensions) · v3.1: B1–B4 + R1–R5 + M1–M3 · v3.2: G1/G1-bis/G2 enforcement · v3.3: I1–I3 integration + M-A through M-F (153 designed tests).
- Schemas: objection, triage, verdict, risk_accepted, skip_incident (v3.3); golden_case (v3.3); outcome, pattern (v3.4).

### Folder documents

- `01_Manual_completo_del_Critico_v1.0.0.md`: consolidation of a broken source (12,282 lines, 13 deliveries) into a professional manual.
- `02_FROZEN_v3.3.md`: freeze record (34 invariants).
- `13_Diseno_Completo_Universal_Critico.md` v1.0.0 → **v1.1.0**: improvement loop (§15), multiple subprofiles (§7.5), 20 macro profiles and 164→**153 subprofiles** after the merger audit (§7.6).
- `14_AUDITORIA_FINAL.md`: round 1 (9 corrections) + round 2 (mergers).
- `16_GATE_B_Autoauditoria.md`: product self-GATE B, **PASA_CON_CONDICIONES** with 6 conditions.

### Assisted-mode tools

- `critico_cli.py`, `prompts/critico_system.md`, seven templates, `README_PRODUCTO.md`, `probar_todo.py` (historical PASS 17/17).
- Loop: `scripts/outcome_runner.py`, `evals/calibration.py`, `evals/patterns.py`, `evals/calibration_panel.py`, `scripts/autopopulate_v1_angle.py`.

### Notable corrections

- Residual `\_` escapes (converter bug); internal monologue removed from the appendix; YAML 1.1 enum `no`→False (outcome/pattern); Python 3.12 f-string made compatible with 3.10; schema count corrected from 9 to 8.

### Round 3 — independent review (external verifier)

- Eight findings accepted and corrected: verdict→outcome contract; unified validators (M1/M2/M3/I3/G5/X1); I3 `required`; overwrite protection in four tools; migration with actual JSON Schema; extension profiles blocked in triage; corrected prompt (terminal RIESGO_NO_EVALUADO); accurate suite records.
- `probar_todo.py` with negative cases → historical **PASS 31/31**.

### Round 4 — second independent review

- Four gaps corrected: ABSENT-field test (delete key); `verificar` validates schemas first; deep M3 (resolved questions + demonstrable hash change); initializer REJECTS incompatible objections (optional `--ignorar-incompatibles`).
- `probar_todo.py` → historical PASS 37/37, including rounds 1–4 negative cases. README qualification: the validator is NOT a technical guarantee until the suite is accredited.

### Pending

- Materialize and execute the 153 designed tests; management decisions in audit §4.

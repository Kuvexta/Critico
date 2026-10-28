# LESSONS LEARNED — Critic (candidates)

[Spanish source](../../LECCIONES_APRENDIDAS.md). Translation dated 2026-10-27.

> Proposed by the independent review of 2026-10-26 (external verifier).
> Status: **not registered and not assigned permanent numbers** — GATE C decides whether to promote them.

| Candidate ID | Lesson | Originating evidence |
|---|---|---|
| LA-xx | Test every workflow with inputs valid under the preceding component's contract. | outcome_runner read verdict.objections, forbidden by the verdict schema; the test used a simplified, unvalidated verdict. |
| LA-xx | Distinguish structural validation, business rules and cross-file consistency. | validar checked only schema; M1/M2/M3/I3/G5 were scattered or unapplied; no triage↔verdict check existed. |
| LA-xx | Clearly separate designed tests, executed tests and demonstrated results. | A record claimed “153 green tests” without execution; probar_todo.py's PASS 17/17 missed contract incompatibilities. |
| LA-xx | JSON Schema if/then must require the conditioning field, or it triggers when that field is omitted. | The I3 condition (GATE_SKIPPED) forced NO_PASA on verdicts without reason_code. |
| LA-xx | File generators must refuse overwrite without --force. | Template, triage, outcome and migration opened outputs in write mode without checking existence. |
| LA-xx | YAML 1.1 turns no/yes into booleans: quote enum values. | materialized: no parsed as False and broke validation. |

*Subsequent changes are versioned.*

## Local closure candidates — 2026-10-26

These lessons originate in CIERRE-CRITICO-01 and its tests; they have neither permanent numbers nor workspace registration.

| Candidate ID | Lesson | Local source |
|---|---|---|
| LA-xx | Authorizing a lot with files, objectives, retries and stopping boundaries permits correction without expanding scope. | CIERRE-CRITICO-01 proposal and authorization transcript. |
| LA-xx | Search existing environments and verify dependencies before modifying code. | ENTORNO-CIERRE-01 and the isolated environment's installation log. |
| LA-xx | An unverifiable test is not a passed test; permission preconditions must be demonstrated. | Read-permission case in RESULTADOS.json. |
| LA-xx | A valid record does not offset an invalid record or resolve ambiguous identity. | M3 valid-plus-invalid and identical-duplicate cases. |
| LA-xx | Sharing validation across entry points prevents an initializer or metric from accepting what the CLI rejects. | G1 and S1 in the coverage matrix. |
| LA-xx | Cleanup must be confined to owned temporary files and reported even after early exit. | TMP1 and REP1 cases. |
| LA-xx | Hash, truth, approval and independence are distinct properties. | Evidence states and documented closure limits. |
| LA-xx | A process's display encoding must not hide an already saved result. | First run: suite succeeded, cp1252 display failed; UTF-8 log preserved. |

## Bilingual lot candidates — 2026-10-27

| Candidate ID | Lesson | Local source |
|---|---|---|
| LA-xx | Translate presentation and internal code without translating external data contracts. | BILINGUE-CRITICO-01, API compatibility map and locale tests. |
| LA-xx | Preserve legacy keyword arguments and exception identity, not just function names. | Compatibility wrappers and bilingual_checks.py. |
| LA-xx | Matching translation structure and hashes supports traceability, not independent semantic certification. | Translation registry and TRANSLATION_REVIEW.md. |

These are candidates only, with no workspace registration.

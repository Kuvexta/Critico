# Kuvexta policy (only when applicable)

[Español](../kuvexta.md).

This reference describes the project's division of responsibilities; it does not authorize workspace access or replace the owning repository's rules.

- Criba checks facts; Critic challenges assumptions; GATE C decides. If you worked on the artifact, disclose the lack of independence and request external review when necessary.
- Terminal states: PASA, PASA_CON_CONDICIONES, NO_PASA, RIESGO_NO_EVALUADO. Suspensions: NECESITA_INFO and REVISION_PARCIAL, with cycle control. Do not confuse suspension with approval or terminal rejection.
- An active skip prevents PASA: I3 requires NO_PASA and GATE_SKIPPED.
- M3 requires resolved questions, an identified suspension and an actual hash change relative to the hash recorded at suspension. A verdict's shape alone does not prove M3.
- Change proposals and their hashes are not approval records. Do not attribute words to the decision maker. Respect the current authorization protocol outside this skill.

## Risk gates (P31)

Risk sets the level of control: reversible work on a branch, pilot or PR = free with CI and review by another tool; merge to a protected branch = Dirección approval in the PR; production, money, deletions, secrets, permissions and policies = Dirección literal. While the Critic is in pilot, its GATE B is advisory at boundaries. Deterministic gates (tests, mutations, scanners, hashes) override the Critic; the Critic flags and escalates.

## The Critic at two levels

| Level | Who | Counts as a gate | Output |
|---|---|---|---|
| **AUTOCONTROL** | The author, in their own session, with the skill | **No** | Improves the delivery before review is requested |
| **INDEPENDIENTE** | A reviewer from another model family, without the author's session, context or memory, and without reading their self-review | Yes (GATE B) | Verdict bound to the exact `artifact_binding` |

**Separation:** nobody reviews what they designed or runs the gate they designed. Independence is demonstrated with the card in [method.md](method.md) §0, not declared.

**Formal record:** recording a GATE B (triage/objection/verdict YAML against the schemas and its log entry) is a **separate task**, with its own assignment; this read-only skill does not create it or claim that it exists.

## AUTOCONTROL protocol

1. Label the output “Critic in session — <date> — AUTOCONTROL, not a gate”.
2. Bind the output to the hash of the reviewed head and the sha256 of the skill used (`SKILL.md` or the skill manifest).
3. Do not use self-review as evidence of approval or cite it as GATE B.
4. If self-review finds a **blocker**, the author **does not declare “READY FOR REVIEW”** until it is fixed (or documented as a blocker for Dirección).

Workspace incorporation belongs to its maintainer. BZ registration, P01 anchoring, check_encargo and P22 are checks of the destination environment, which its maintainer must consult and execute there. This package neither claims to know their state nor performs them.

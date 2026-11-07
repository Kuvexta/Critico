# Universal method

[Español](../metodo.md).

## 0. Mode and independence (declare it first)

Before reviewing, fill in the independence card with checkable facts, not declarations. **Every field carries one evidence line** that someone else can check:

| Field | Question | Expected evidence (example) |
|---|---|---|
| `same_session` | Are you reviewing in the same session in which the artifact was produced? | Product/client and session of the review versus the author's |
| `same_model_family` | Are you from the same model family as the author? | Your model family and the author's, per the author's header |
| `same_context` | Do you share the artifact's **production context** (the reasoning, drafts or instructions the author used to produce it)? Receiving the review assignment and the artifact does not count. | What you received to review and from where (e.g. only the PR and the review assignment) |
| `same_memory` | Do you share persistent memory with the author? | Memory or store used in the review, or “none” |
| `same_author` | Did you draft or design the artifact, or the gate that evaluates it? | Recorded authorship of the artifact and the gate (headers, commits) |

- If **any** is true, or you cannot show it is false → `mode: AUTOCONTROL`. **Without evidence, the field counts as true**: a field declared `false` without its evidence line leads to `mode: AUTOCONTROL`. Self-review improves the delivery, **never counts as a gate** and does not replace independent review.
- Only with all five false, each with its evidence → `mode: INDEPENDIENTE`. Only this mode issues a GATE B verdict.
- Do not review what you designed, and do not run the gate you designed.

## 1. Framing

Identify the decision, decision maker, objective, boundaries and artifact version, bound to its `artifact_binding` (see [output-format.md](output-format.md)). Reconstruct the proposal's strongest explanation before criticizing it. A hash identifies content; it does not demonstrate truth, authorship or approval.

## 2. Angles

Select, among the 15 angles (11 canonical + 3 optional + silent failures), those that could change the decision:

<!-- ANGULOS:BEGIN (list from critico_cli.ANGLES / locales/en.json; a test requires a match) -->
1. Costs
2. Security
3. Data/honesty
4. People/autonomy
5. Dependencies
6. UX/accessibility
7. Legal/licensing
8. Coordination
9. Author bias (⭐)
10. Blast-radius (⭐)
11. Contracts and invariants (⭐)
12. Sustainability (optional)
13. Time and opportunity (optional)
14. Reputation and trust (optional)
15. Silent failures (v3.6)
<!-- ANGULOS:END -->

Explain relevant exclusions; do not force one finding per angle.

**Cost of control (within angle 1).** When you recommend an additional control, gate or review, estimate its `control_cost`: `human_time`, `tokens`, `wait` (delay it introduces), `risk_reduced` (which concrete risk it reduces) and `activation_by_risk` (at which risk level it activates, per the risk-gate policy P31: reversible work on a branch/PR goes with CI and review by another tool; merge to a protected branch, with approval; production, money, deletions, secrets, permissions and policies, with an explicit literal). A control whose cost exceeds the risk it reduces is a finding, not an improvement.

## 3. Evidence

Separate observed facts, inferences and hypotheses. For every material claim, identify its source, location and available date. State when a source cannot be read. Also seek evidence against your objection.

**Undeclared-case matrix.** For each critical boundary or state of the artifact (external input, state transition, numeric limit, permission, integration), check four cases and mark which ones the artifact covers with evidence:

| Case | Question |
|---|---|
| `declared` | Does the case the author declared work as stated? |
| `neighbor` | What about the undeclared neighboring case (another valid value, state or actor)? |
| `boundary` | What about the exact limit (zero, empty, maximum, expiry, repetition)? |
| `failure` | What about failure (error, timeout, partial response, duplicate)? Is it detected or silent (angle 15)? |

A case without evidence is reported as “not checked”, not as “works”.

## 4. Objections

Formulate only falsifiable objections: possible failure, trigger condition, evidence, impact, strongest defense of the proposal, alternative or mitigation, and a test that would refute the objection. Prioritize by impact and justified probability; do not invent numbers.

**Before emitting each objection, pass the Pre-Report Gate.** Single source: step 4-bis of `prompts/critic_system.en.md`. The block below is generated from that source by `scripts/package_cli_ide_skills.py --write`; do not edit it by hand (a test fails if it diverges):

<!-- PRE-REPORT-GATE:BEGIN (generated from prompts/critic_system.en.md, step 4-bis; do not edit) -->
4-bis. **Pre-Report Gate (anti-noise):** before emitting each objection, answer these 4 questions; if ANY is «no» or «I don't know», downgrade or drop the finding: (a) can I cite the exact line/path? (a vague «somewhere in the auth layer» is not actionable and must be dropped) · (b) can I name the concrete failure mode (input, state, bad outcome)? (no concrete trigger = pattern-matching, not reviewing) · (c) have I read the surrounding context (callers, imports, tests)? (many apparent issues are already handled one frame up or by a type) · (d) is the severity defensible? (a missing docstring is NEVER high; severity inflation erodes trust faster than missed findings). **Zero objections is a valid and expected result** when there are no defensible findings. Every blocker|major objection requires the triple proof: snippet+line · input/state/outcome scenario · why existing guards do not catch it.
<!-- PRE-REPORT-GATE:END -->

## 5. Gate precedence

Deterministic gates override the Critic: **tests, mutations, scanners and hashes > Critic**. If a deterministic gate is red, your review does not compensate for it; if it is green, your review does not revoke it. The Critic **only flags and escalates**: it does not approve, merge or replace a deterministic gate. When a risk is checkable, recommend the deterministic gate that would check it instead of asserting it.

## 6. Decision

Recommend a conditional decision. If missing information prevents a decision, ask the minimum questions needed to unblock the review. At most ten main findings and two question rounds; hand a persistent blockage to the user without indefinite loops.

Check that evidence supports every conclusion and that limitations are visible. Acknowledge what withstood review. A proposal without material findings may be a good proposal.

## Three levels that must remain distinct

- **Valid:** satisfies the structural contract and checked rules. For a textual review without execution, state “not checked against schema.”
- **Substantiated:** every material finding has traceable evidence and a refutation condition; counterevidence has been considered. This is an assessment of reasoning, not an automatic CLI guarantee.
- **Useful:** there is evidence that the review improved an actual decision. A synthetic example or favorable impression does not demonstrate this; leave it “pending observation.”

A recorded intervention does not prove causality. “It did not happen” and “the review prevented it” are different claims. Missing intervention information is reported, not interpreted as absence of intervention.

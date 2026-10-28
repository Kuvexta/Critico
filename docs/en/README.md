# Critic — local assisted version

[Spanish source](../../README_PRODUCTO.md). Translation dated 2026-10-27.

**Project author: KUVEXTA GROUP.** See [AUTHORSHIP.md](AUTHORSHIP.md).

Documentation update of 2026-10-27: the [license catalogue](licensing/README.md) contains reference texts, comparisons and drafts for a later decision. **No new alternative is active.** The existing abbreviated LICENSE declaration is preserved and requires review before distribution.

The preceding package is `entrega/licencias-v1/critico-con-opciones-licencia-v1.zip`; its manifest is `entrega/licencias-v1/MANIFIESTO_SHA256.json`. The closure-v1 manifests and results are historical evidence for the code tested then. In that ZIP, original reports remain under `entrega/` and the license-update report under `entrega/licencias-v1/`. Its checks were documentary and integrity checks, not a rerun of the suite.

State as of 2026-10-26: local implementation with a reproducible suite and a manual read-only skill. Rubric and configuration remain 3.3.0; the eight schemas retain their v3.2–v3.4 identifiers. That closure tightened runtime validation and tracking; it is not represented as fully compatible with inputs formerly accepted.

Critic helps review a proposal's assumptions before a decision. Evidence, judgment and human authorization remain necessary. Schema validity does not demonstrate truth or usefulness.

## Start with the skill

The `skills/critico/` folder contains self-contained instructions and references. Invocation is manual and its work is read-only: it produces a chat review. It installs nothing and writes no records. Codex metadata includes `allow_implicit_invocation: false`. Installation in any application belongs to the destination maintainer.

Four layers remain separate: universal method, optional Kuvexta policy, contracts/CLI, and destination integration. [The contextual prompt](../../prompts/critic_system.en.md) describes Kuvexta. It is not mandatory for universal review.

## CLI and local environment

Python >=3.10, PyYAML and jsonschema are assisted-mode dependencies; pytest is declared for future suites. The preceding delivery was exercised on Python 3.14.7, Windows, with exact versions in its DEPENDENCIAS.txt. No platform matrix is accredited.

An isolated environment was prepared in this development folder. In PowerShell:

```powershell
& .\.entorno-cierre\venv\Scripts\python.exe -B -X utf8 run_tests.py --lang en
```

The environment is not distributed in the ZIP. The migrator must create one under destination rules. The package does not install dependencies or code globally.

Example workflow (replace `python` with the environment interpreter):

```text
python -B -X utf8 critico_cli.py triage --artifact PROP-042 --profile business --lang en
python -B -X utf8 critico_cli.py validate --triage triage-PROP-042.yaml --draft --lang en
```

The generator produces a **draft**, not an operational triage: complete dates, dimensions, counts and references. `--draft`/`--borrador` checks structure only; it does not check dates, placeholders or operational rules. Templates are supplied as drafts.

After completing triage, objections and verdict:

```text
python -B -X utf8 critico_cli.py validate --triage triage-PROP-042.yaml --objection objection.yaml --verdict verdict.yaml --lang en
python -B -X utf8 critico_cli.py verify --triage triage-PROP-042.yaml --verdict verdict.yaml --artifact proposal.txt --log verdicts.jsonl --lang en
python -B -X utf8 scripts/outcome_runner.py init --verdict verdict.yaml --objections objection.yaml --horizon corto_plazo --lang en
```

`verify` requires an artifact file and an existing log (which may be empty if there is no reset). M3 looks for a unique, valid suspension of the correct artifact, requires resolved questions and a current hash different from the recorded hash. The declared historical hash is neither a signature nor certification of the log.

The initial outcome is also a draft. Complete date, evidence and provenance before:

```text
python -B -X utf8 scripts/outcome_runner.py validate --outcome outcome-PROP-042.yaml --lang en
python -B -X utf8 scripts/outcome_runner.py metrics --log outcomes.jsonl --by profile --lang en
```

Metrics reject invalid records before calculating. Interventions are grouped by `verdict_id`; null/missing means unreported. Several horizons can contribute several observations: prediction metrics remain observation-based, while intervention is decision-based. Causality is not inferred.

## Contracts and limitations

- `validate`: schema, operational dates, placeholders and local rules. It is not equivalent to `verify` for M3.
- `verify`: triage/verdict consistency and reset evidence; any invalid historical record is rejected. Duplicate suspensions require disambiguation outside this tool.
- Tracking: `completo` and `omitidos` must agree. Deliberate omission remains partial tracking.
- Evidence: HASH_VERIFICADO means content correspondence. Remote, inaccessible or hashless evidence is NO_VERIFICADO. Only a hash mismatch rejects in this check. Relative evidence paths and `validate --artifact` paths are based on the document directory. `verify --artifact` uses the command's path.
- Dates: date/time with timezone and a valid calendar is required. There is no automatic freshness policy, source reputation or log authentication yet.
- Migration: real schema validation, visible quarantine, revalidation of previously migrated records and preserved input. Do not migrate actual data without the corresponding assignment.

## Closure evidence

The suite distinguishes passed, failed and not verifiable checks; a failure or incomplete cleanup returns code 1. It writes only owned temporary files, directs child temporary files there and disables bytecode. It does not clean old caches or the temporary parent directory. CLI artifact-creation commands do write to their explicit destinations: read-only behavior belongs to the skill.

Historical exact results and source hashes are in closure-v1's RESULTADOS.json, with coverage in MATRIZ_COBERTURA.csv. The pilot is synthetic; it validates neither real decisions nor production usefulness. Its review and tests were performed by the implementing agent, not an independent ratifier.

The historical 153 tests remain unmaterialized. `07_Makefile` and `08_critico-ci.yml` are historical references, not active CI. This suite does not claim full accreditation of the design's 34 invariants.

Historical incidents and authorizations retain their state; technical closure does not resolve them retroactively. Kuvexta migration, BZ registration, P01, check_encargo and P22 belong to the destination maintainer. This lot did not access the workspace.

## Bilingual delivery — 2026-10-27

English internals retain legacy interfaces through aliases/wrappers. English and Spanish presentation share one engine. [Language selection](../LANGUAGES.md) and [API compatibility](../API_COMPATIBILITY.md) document the stable boundaries. The suite now uses owned `_tmp_pruebas/run-bilingual-<pid>-<uuid>/` roots.

The intended package is `entrega/bilingue-v1/critico-bilingual-v1.zip`, with REPORT.en.md, RESULTS.json, COVERAGE.csv and MANIFEST_SHA256.json. Consult those artifacts for the final state and actual tests; the historical results above are not current acceptance.

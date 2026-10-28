# El Crítico — local delivery entry point

[Spanish source](../../LEEME.md). Translation dated 2026-10-27. The original reference date is 2026-10-26; the bilingual delivery update follows below.

1. Read [README.md](README.md) for current usage and limits.
2. Use [the skill](../../skills/critico/SKILL.md) for manual, read-only review.
3. Consult the historical closure report and results under `entrega/cierre-v1/` in the development folder for that lot's verified state, incidents and pending work.
4. The original handoff package was `entrega/cierre-v1/critico-cierre-v1.zip`, accompanied by its SHA-256. The bilingual package supersedes it for the present handoff.

## Package map

- `critico_cli.py`, `critico_cli.py`, `evals/`, `scripts/` and `06_migration/`: local tools.
- `03_rubric.yaml`, `04_critic.config.yaml`, `05_schema/`: rubric, configuration and eight schemas.
- `templates/`: seven drafts that must be completed for operational use.
- `skills/critico/`: universal method and separate Kuvexta reference.
- [Kuvexta prompt](../../prompts/critic_system.en.md): contextual prompt without execution or write permission.
- Manual, freeze and universal design: design references, not evidence of complete coverage.
- [CHANGELOG.md](CHANGELOG.md) and [LESSONS_LEARNED.md](LESSONS_LEARNED.md): history and candidate lessons.
- `requirements.txt` and `LICENSE`: requirements and license.

The development folder retains audits, proposals and historical materials that are not part of the ZIP. Do not confuse their old results with the current delivery. The `.entorno-cierre` environment, existing caches and temporary files are not distributed.

## Verification

With an environment already prepared and authorization to create/clean its owned temporary files:

```powershell
& .\.entorno-cierre\venv\Scripts\python.exe -B -X utf8 run_tests.py --lang en
```

Do not use `py_compile` for read-only inspection: it generates bytecode. This lot's syntax checks compile in memory.

Workspace incorporation is its maintainer's responsibility. This package does not install a skill, activate a plugin, publish anything or execute remote CI.

## Bilingual delivery — 2026-10-27

The intended handoff is `entrega/bilingue-v1/critico-bilingual-v1.zip`. Consult its REPORT.en.md, RESULTS.json and MANIFEST_SHA256.json for actual acceptance, source hashes and limitations. Earlier reports remain historical. [Language selection and stable contracts](../LANGUAGES.md).

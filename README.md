# Crítico — metodología congelada de análisis, GATE B y gobernanza

**¿Qué es?** El Crítico convierte una propuesta, decisión o documento en un
expediente auditable (GATE B): **triage** con dimensiones activas, **objeciones
falsables** (cada una con su steelman —la versión más fuerte de lo que ataca—,
supuestos contrastados, contrafactual, condición de falsación, severidad y
confianza), **veredicto** (PASA / PASA_CON_CONDICIONES / NO_PASA) y
**seguimiento de outcomes** con métricas (surprise_rate, calibración). Principio
rector: **nada se simula y nada se declara demostrado sin evidencia
verificable** (diseñado ≠ demostrado).

- **Release del repositorio: `01.00.01`** (etapa DEFINITIVO · regla 00/01)
- **Metodología congelada: `v3.6.0`** (rúbrica de 108 dimensiones, 8 esquemas y config — verificada por `verify_freeze`)

> **Mapeo de versiones (C2):** `VERSION` contiene el release del repo
> (`01.00.01`); `04_critic.config.yaml → critic_version` contiene la versión de
> la metodología congelada (`3.6.0`). El release definitivo `01.00.00` quedó
> CORTADO el 2026-10-29, junto al **Banco Universal de Pruebas (BUP)**
> (https://github.com/Kuvexta/BUP) — gates cerrados y suite 166/166 en verde.

## Requisitos

- Python **≥ 3.10**
- `pip install -r requirements.txt` (`pyyaml>=6.0`, `jsonschema>=4.20`)

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `critico_cli.py` · `critic_i18n.py` · `probar_todo.py` · `run_tests.py` | CLI, i18n y batería (regresión compartida) |
| `03_rubric.yaml` · `04_critic.config.yaml` | Rúbrica de 108 dimensiones y configuración congelada |
| `05_schema/` · `templates/` · `prompts/` · `locales/` | Esquemas, plantillas, prompts e idiomas (es/en) |
| `skills/critico/` | Skill de **solo lectura** para asistentes (invocación manual) |
| `commands/` | Comandos slash para OpenCode (`/ojocritico` y 13 alias) |
| `evals/` · `scripts/` · `09_golden_set/` · `06_migration/` | Validadores, métricas, herramientas, golden set y migración |
| `01_Manual_…` · `02_FROZEN_v3.4.md` · `13_Diseno_…` | Manual, referencia congelada y diseño universal |
| `docs/HASHES.md` | Registro central de hashes de documentos |

> Los **registros de gobernanza** (propuestas, actas, entregas) no están en este
> repositorio público: se conservan en un archivo privado fuera de él; las rutas
> `registros/…` citadas en el CHANGELOG apuntan a ese archivo.

## Uso — GATE B en 6 pasos

```bash
# 1 · Triage: generar el borrador y completarlo con tus dimensiones activas
python3 critico_cli.py triage --artefacto MI-DOC --perfil tech --sub tech.design

# 2 · Objeciones (2–4 propias) y veredicto
python3 critico_cli.py plantilla --tipo objecion
python3 critico_cli.py plantilla --tipo verdict

# 3 · Validación de cada pieza (corrige hasta exit 0)
python3 critico_cli.py validar --triage triage.yaml
python3 critico_cli.py validar --objecion obj1.yaml   # una por cada objeción
python3 critico_cli.py validar --verdict verdict.yaml

# 4 · Coherencia cruzada con el artefacto real (crea antes la bitácora vacía)
python3 critico_cli.py verificar --triage triage.yaml --verdict verdict.yaml \
        --artefacto <archivo-revisado> --bitacora bitacora.jsonl

# 5 · Outcome (seguimiento de objeciones) y métricas
python3 scripts/outcome_runner.py init --verdict verdict.yaml --objeciones obj1.yaml obj2.yaml
python3 scripts/outcome_runner.py metricas --bitacora bitacora.jsonl
```

**Otros comandos del CLI** (`python3 critico_cli.py --help`): `validar
--outcome`, `plantilla --tipo triage|objecion|verdict|outcome|…`, `perfiles`
(lista macro-perfiles y sub-perfiles con su guía de dimensiones) y `hash`
(SHA-256 de un archivo para evidencias).

## Dimensiones y perfiles

- **108 dimensiones** en la rúbrica congelada (`03_rubric.yaml`); el triage
  activa un subconjunto (máx. 40) elegido por el revisor.
- **Macro-perfiles** (6 congelados: `tech`, `ops`, `legal`, `business`, `personal`, `health`) con **sub-perfiles**
  (`tech.design`, `tech.migration`, …): `triage --sub <sub>` imprime su guía
  **no vinculante** de dimensiones; `perfiles` lista todos.

## Reglas (gobernanza)

- Rúbrica, esquemas y config **congelados en v3.6.0**: cualquier cambio exige
  propuesta numerada con protocolo y la frase canónica de autorización
  **«OK <8hex>»** (o mandato global de Dirección registrado), más la
  actualización del freeze.
- Los registros no se editan: una corrección es una **adenda** que referencia
  el original por hash.
- Los borrados los ejecuta el **responsable designado por Dirección** (encargado de la dirección o responsable del proceso; perfil inicial: Andrés), por ítem, con hash y acta.
- Batería actual del repo: **100/100** · suite de **166 tests**:
  materializada (166/166) con ratchet en CI (`docs/SUITE_BASELINE`).

## Límites honestos

- Herramienta de análisis **defensivo**; no sustituye la decisión humana: las
  autorizaciones y decisiones son siempre del usuario.
- Una revisión textual con la skill **no certifica** cumplimiento de esquemas;
  eso exige correr el CLI sobre el artefacto real.
- **Sin certificación independiente declarada**: lo que no se demuestra, se
  declara como pendiente.

## Nota sobre scripts históricos

`scripts/{autopopulate_v1_angle,empaquetar_cierre,empaquetar_licencias,package_bilingual,package_cli_ide_skills}.py`
son de **entregas históricas**: tres corresponden a paquetes ya consumidos y
dos (`empaquetar_cierre`, `empaquetar_licencias`) referencian archivos del
archivo privado retirados del repo público (inventario en Kuvexta/Ecosistema).

## Comunidad (repositorio público)

- **Etapa: definitivo (`01`)** — release 01.00.00 CORTADO (2026-10-29); lo no demostrado se sigue
  declarando como pendiente.
- **Licencia:** código MIT · documentación CC BY-SA 4.0 (ver `LICENSE`).
- **Skill para OpenCode (distribución principal):** copiar `skills/critico/` a
  `~/.config/opencode/skills/critico/` (Linux/macOS) o
  `%USERPROFILE%\.config\opencode\skills\critico` (Windows).
- **Variantes por plataforma (`plataformas/`):** el mismo Crítico empaquetado
  para 12 clientes más una variante universal; cada carpeta incluye su
  README con la ruta exacta de instalación, LICENSE y AUTORIA:

| Plataforma | Carpeta | Destino de proyecto |
|---|---|---|
| OpenCode | `plataformas/opencode` | `.opencode/skills/critico` |
| Claude Code | `plataformas/claude-code` | `.claude/skills/critico` |
| Cursor | `plataformas/cursor` | `.cursor/skills/critico` |
| OpenAI Codex | `plataformas/codex` | `.agents/skills/critico` |
| Cline | `plataformas/cline` | `.cline/skills/critico` |
| Gemini CLI | `plataformas/gemini-cli` | `.gemini/skills/critico` |
| GitHub Copilot | `plataformas/github-copilot` | `.github/skills/critico` |
| Kiro | `plataformas/kiro` | `.kiro/skills/critico` |
| OpenClaw | `plataformas/openclaw` | `skills/critico` |
| Qwen Code | `plataformas/qwen-code` | `.qwen/skills/critico` |
| DeepSeek Harness | `plataformas/deepseek-harness` | `.dsh/skills/critico` |
| Antigravity (Google) | `plataformas/antigravity` | `.agents/skills/critico` |
| Universal (otros clientes) | `plataformas/universal` | raíz de skills del cliente |

  Las variantes provienen de la entrega `skills-cli-ide-v1` (manifiesto
  SHA-256 `3b0a0e3e…`): mismas comprobaciones 172/172, sin scripts, sin
  MCP, sin hooks; instalación y permisos corresponden a cada destino.
  **Instala una sola variante** (la de tu cliente); no copies toda la carpeta
  `plataformas/` a una raíz de descubrimiento automático.
- **Comandos slash:** copiar `commands/*.md` a `~/.config/opencode/command/`
  (Linux/macOS) o `%USERPROFILE%\.config\opencode\command` (Windows); quedan
  disponibles como `/ojocritico`, `/ojo-critico`, `/critico`, `/gateb`,
  `/premortem`, `/punto-ciego`, `/revision-critica`, `/devils-advocate`,
  `/challenge-review`, `/critical-eye`, `/steelman`, `/falsabilidad`,
  `/falsifiability` y `/argumento-de-acero` (alias del mismo Crítico; la skill
  mantiene el id `critico`).
- **Para contribuir:** `CONTRIBUTING.md` (mapa de archivos, congelado y flujo
  de propuestas CAMBIO).
- **Para agentes:** `AGENTS.md` orienta a cualquier agente que trabaje con
  este repositorio (entrada rápida, reglas, instalación).
- **Repos hermanos:** BUP https://github.com/Kuvexta/BUP · Videoteca
  https://github.com/Kuvexta/videoteca

# Crítico — metodología congelada de análisis, GATE B y gobernanza

- **Release del repositorio: `00.02.03`** (etapa construcción · regla 00/01)
- **Metodología congelada: `v3.4.0`** (rúbrica, esquemas y config — verificada por `verify_freeze`)

> **Mapeo de versiones (C2):** `VERSION` contiene el release del repo
> (`00.02.03`); `04_critic.config.yaml → critic_version` contiene la versión de
> la metodología congelada (`3.4.0`). El release definitivo `01.00.00` se
> emitirá cuando el **Banco Universal de Pruebas (BUP)**
> (https://github.com/Kuvexta/BUP) esté listo y la suite completa pase sobre él.

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `critico_cli.py` · `critic_i18n.py` · `probar_todo.py` · `run_tests.py` | CLI, i18n y batería (regresión compartida) |
| `03_rubric.yaml` · `04_critic.config.yaml` | Rúbrica de 108 dimensiones y configuración congelada |
| `05_schema/` · `templates/` · `prompts/` · `locales/` · `skills/` | Esquemas, plantillas, prompts, idiomas y skill de solo lectura |
| `evals/` · `scripts/` · `09_golden_set/` · `06_migration/` | Validadores, métricas, herramientas, golden set y migración |
| `01_Manual_…` · `02_FROZEN_v3.4.md` · `13_Diseno_…` | Manual, referencia congelada y diseño universal |
| `registros/` | **Registros inmutables** (ID+hash): propuestas, entregas, licencias, actas — corrección solo por adenda |
| `docs/HASHES.md` | Registro central de hashes de documentos |

## Uso

```
PYTHONDONTWRITEBYTECODE=1 python3 -B critico_cli.py --help
PYTHONDONTWRITEBYTECODE=1 python3 -B probar_todo.py
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_freeze.py
```

## Reglas

- Rúbrica, esquemas y config **congelados en v3.4.0**; cualquier cambio exige
  propuesta numerada con protocolo (OK-escribir/OK) y actualización del freeze.
- Los **registros** no se editan: una corrección es una adenda que referencia el
  original por hash.
- Los borrados los hace Andrés, por ítem con hash y acta.
- Suite histórica de 153 tests: pendiente hasta que el banco BUP esté listo.

## Comunidad (repositorio público)

- **Etapa: construcción `00.02.03`** — beta honesto: lo no demostrado se declara;
  el release definitivo `01.00.00` llegará cuando el Banco Universal de Pruebas
  (BUP) esté listo y la suite completa pase.
- **Licencia:** código MIT · documentación CC BY-SA 4.0 (ver `LICENSE`).
- **Gobernanza:** los registros de gobernanza (propuestas, actas, entregas) se
  conservan en un archivo privado fuera de este repositorio; las rutas
  `registros/…` citadas en el CHANGELOG apuntan a ese archivo.
- **Skill para OpenCode:** copiar `skills/critico/` a
  `~/.config/opencode/skills/critico/` (Linux/macOS) o
  `%USERPROFILE%\.config\opencode\skills\critico` (Windows).
- **Comandos slash:** copiar `commands/*.md` a `~/.config/opencode/command/`
  (Linux/macOS) o `%USERPROFILE%\.config\opencode\command` (Windows);
  quedan disponibles como `/ojocritico`, `/ojo-critico`, `/critico`, `/gateb`,
  `/premortem`, `/punto-ciego`, `/revision-critica`, `/devils-advocate`,
  `/challenge-review`, `/critical-eye`, `/steelman`, `/falsabilidad`,
  `/falsifiability` y `/argumento-de-acero` (alias del mismo Crítico; la skill
  mantiene el id `critico`).

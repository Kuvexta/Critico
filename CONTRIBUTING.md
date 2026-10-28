# CONTRIBUTING — cómo aportar al Crítico

El Crítico acepta mejoras de la comunidad, pero **no recibe cambios directos**:
toda mejora llega como una **propuesta numerada** (CAMBIO) que decide
**Andrés** (raíz de autorización) con la frase canónica **«OK <8hex>»**. Este
documento explica qué vive dónde, qué está congelado y cómo se presenta una
propuesta.

## Mapa: qué se actualiza dónde

| Si quieres… | Archivo(s) | Congelado |
|---|---|---|
| Añadir/mejorar **dimensiones** de la rúbrica | `03_rubric.yaml` (niveles, evidencia, v1_angle) | **Sí** (v3.4.0) → CAMBIO + `critic_version` + freeze |
| Añadir/mejorar **perfiles y sub-perfiles** (p. ej. `tech.design`) | `04_critic.config.yaml` → `profiles.universals.<macro>.sub_profiles` con `suggested_dimensions` y `keywords` + recalcular `config_hash` | **Sí** → CAMBIO + freeze |
| Registrar **brechas conocidas** | `04_critic.config.yaml` → `known_gaps` | **Sí** → CAMBIO |
| Cambiar los **esquemas** de triage/objeciones/veredicto/outcome | `05_schema/*.yaml` (+ versión en `$id`) | **Sí** → CAMBIO + freeze |
| Cambiar las **reglas locales** de validación | `evals/validators.py` | **Sí** → CAMBIO (su SHA-256 está en el freeze) |
| Mejorar el **CLI**, i18n o scripts | `critico_cli.py`, `critic_i18n.py`, `locales/`, `scripts/` | No → CAMBIO + batería |
| Añadir **casos de la batería** | `probar_todo.py` (+ `tests/` si se materializa) | No → CAMBIO + batería |
| Mejorar la **skill y los comandos** | `skills/critico/`, `commands/`, `plataformas/` | **No** (capa comunitaria, fuera del freeze) |
| Corregir **documentación** | `01_Manual_…`, `02_FROZEN_v3.4.md`, `13_Diseno_…`, `docs/`, `README.md`, `AGENTS.md`, `LEEME.md` | No → CAMBIO documental + `docs/HASHES.md` |
| Actualizar el **golden set** | `09_golden_set/` | No → CAMBIO + batería |

**Regla de oro:** rúbrica, esquemas y config congelados en **v3.4.0**;
cualquier cambio exige CAMBIO numerado, autorización y actualización del
freeze (`scripts/verify_freeze.py` debe quedar en verde).

## Cómo presentar una propuesta (flujo)

1. **Escribe la propuesta** como JSON con, al menos: `id` (CAMBIO-NN),
   `titulo`, `archivos` (los que toca), `detalle` (qué cambia exactamente en
   cada uno), `no_toca` (lo que queda intacto), `validacion` (cómo se
   comprueba: batería, freeze, casos de aceptación) y `autorizacion`.
   Plantilla de referencia: los CAMBIOs citados en el `CHANGELOG.md`.
2. **Ábrela como issue** en este repositorio (o PR con la propuesta y los
   diffs propuestos, sin aplicarlos al congelado por tu cuenta).
3. **Andrés decide**: con la frase «OK <8hex>» (hash de la propuesta). Sin
   esa frase, la propuesta no se aplica.
4. Tras la autorización, la aplicación incluye: cambios + batería
   (`PYTHONDONTWRITEBYTECODE=1 python3 -B probar_todo.py`) + freeze +
   `docs/HASHES.md` + `CHANGELOG.md` + `VERSION` — todo verificado por la
   guarda `scripts/verificar_release.py` — y la **sincronización de las
   copias de trabajo** con `scripts/sincronizar_copias.py --aplicar`
   (producción y workspace; dry-run primero).

## Ejemplo: añadir un sub-perfil

Propuesta `CAMBIO-NN` que declara:

- `04_critic.config.yaml`: añadir a `profiles.universals.tech.sub_profiles`
  la entrada `tech.<nombre>` con `suggested_dimensions` (ids 1..108 de
  `03_rubric.yaml`) y `keywords`; recalcular `config_hash` (SHA-256 canónico
  del fichero excluyendo el propio campo).
- `no_toca`: `03_rubric.yaml`, esquemas, código, batería.
- `validacion`: `verify_freeze` en verde + batería completa + conteo de
  sub-perfiles coherente + cada `suggested_dimensions ⊆ 1..108`.

## Qué pasa cuando una propuesta se acepta

1. En el issue/PR se deja la etiqueta de decisión y un **comentario de cierre**
   con el `CAMBIO-NN` definitivo y el SHA-256 de la propuesta.
2. La propuesta oficial se registra en el **archivo privado de gobernanza**
   (fuera de este repositorio, junto con la frase de autorización).
3. El cambio se aplica, verifica (batería + freeze + guarda) y sincroniza a
   las copias de trabajo; `CHANGELOG.md`, `docs/HASHES.md` y `VERSION` quedan
   actualizados.

## Límites honestos de una contribución

- Los **registros de gobernanza** (propuestas históricas, actas, entregas)
  viven en un archivo privado: no los reproduzcas ni los inventes.
- **Nada se simula**: una capacidad añadida se declara; «validado» exige
  evidencia con atestación.
- Las **decisiones** (aplicar, rechazar, revertir) son siempre de Andrés.
- El release definitivo `01.00.00` espera a que el Banco Universal de Pruebas
  (BUP, https://github.com/Kuvexta/BUP) esté listo y la suite histórica de
  153 tests pase.

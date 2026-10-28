# LECCIONES APRENDIDAS — Crítico (candidatas)

> Propuestas por la revisión independiente del 26/10/2026 (verificador externo).
> Estado: **sin registrar ni asignar números definitivos** — GATE C decide si las promueve.

| ID candidato | Lección | Evidencia que la originó |
| :---- | :---- | :---- |
| LA-xx | **Probar cada flujo con entradas válidas según el contrato del componente anterior.** | outcome_runner leía `verdict.objections`, campo que el esquema de veredicto prohíbe — la prueba usaba un veredicto simplificado sin validar |
| LA-xx | **Distinguir validación de estructura, reglas de negocio y coherencia entre archivos.** | `validar` solo comprobaba esquema; las invariantes M1/M2/M3/I3/G5 vivían dispersas o no se aplicaban; no existía chequeo triage↔verdict |
| LA-xx | **Separar claramente pruebas diseñadas, pruebas ejecutadas y resultados demostrados.** | El acta afirmaba «153 tests en verde» sin ejecución; el PASS 17/17 de `probar_todo.py` no cubría las incompatibilidades de contrato |
| LA-xx | **Los `if/then` de JSON Schema deben exigir presencia del campo condicionante (`required`), o disparan con el campo omitido.** | La condición I3 (GATE_SKIPPED) obligaba NO_PASA a veredictos sin `reason_code` |
| LA-xx | **Todo generador de archivos debe negarse a sobrescribir sin `--force`.** | `plantilla`, triage, outcome y migración escribían en modo `w` sin comprobar existencia |
| LA-xx | **YAML 1.1 convierte `no`/`yes` en booleanos: comillar en enums.** | `materialized: no` se parseaba como `False` y rompía la validación |

*Lo que venga, se versiona.*

## Candidatas del cierre local — 26/10/2026

Estas lecciones proceden de CIERRE-CRITICO-01 y sus pruebas; no tienen numeración definitiva ni registro en el workspace.

| ID candidato | Lección | Fuente local |
|---|---|---|
| LA-xx | Autorizar un lote con archivos, objetivos, reintentos y límites de parada permite corregir sin ampliar el alcance. | Propuesta CIERRE-CRITICO-01 y transcript de autorización |
| LA-xx | Buscar entornos existentes y verificar dependencias antes de comenzar a modificar código. | ENTORNO-CIERRE-01 y `.entorno-cierre/instalacion.log` |
| LA-xx | Una prueba no comprobable no es una prueba aprobada; una condición previa de permisos debe demostrarse. | Caso de lectura por permisos en RESULTADOS.json |
| LA-xx | Un registro válido no compensa otro inválido ni resuelve una identidad ambigua. | Casos M3: válido más inválido y duplicado idéntico |
| LA-xx | Compartir la validación entre entradas evita que un inicializador o métrica acepte lo que el CLI rechaza. | G1 y S1 en la matriz de cobertura |
| LA-xx | La limpieza debe limitarse a temporales propios y reportarse incluso tras una salida anticipada. | Casos TMP1 y REP1 |
| LA-xx | Hash, veracidad, aprobación e independencia son propiedades distintas. | Estados de evidencia y límites documentados en CIERRE.md |
| LA-xx | La codificación del proceso que presenta un resultado no debe ocultar el resultado ya guardado. | Primera corrida: batería exitosa, presentación cp1252 fallida; log UTF-8 preservado |

## Candidatas del lote bilingüe — 27/10/2026

| ID candidato | Lección | Fuente local |
|---|---|---|
| LA-xx | Traducir presentación y código interno sin traducir contratos de datos externos. | BILINGUE-CRITICO-01, mapa de API y pruebas de idiomas |
| LA-xx | Conservar argumentos por nombre y la identidad de excepciones, no solo nombres de funciones. | Wrappers y bilingual_checks.py |
| LA-xx | La estructura y los hashes de traducciones aportan trazabilidad, no certificación semántica independiente. | Registro de traducciones y TRANSLATION_REVIEW.md |

## Candidatas del cierre v2 — 28/10/2026

| ID candidato | Lección | Fuente local |
|---|---|---|
| LA-xx | Un paquete de revisión aislada debe incluir todos los archivos necesarios para acreditar los cambios sometidos al gate. | Objeción GATE C 2026-10-28 sobre cierre-v2: faltaban en el ZIP `docs/API_COMPATIBILITY.md` y `scripts/package_bilingual.py` (R-FIX-08) |

Son candidatas, sin registro en el workspace. [English](docs/en/LESSONS_LEARNED.md).

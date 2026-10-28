# Crítico — versión asistida local, cierre-v1

**Autor del proyecto: KUVEXTA GROUP.** Véase [AUTORIA.md](AUTORIA.md).

Actualización documental del 27/10/2026: [catálogo de licencias](licencias/README.md) con textos de referencia, comparativa y borradores para decidir más adelante. **Ninguna alternativa nueva está activada.** La declaración abreviada existente en LICENSE se conserva y requiere revisión antes de distribuir.

El paquete actualizado está en `entrega/licencias-v1/critico-con-opciones-licencia-v1.zip`. Su manifiesto vigente está en `entrega/licencias-v1/MANIFIESTO_SHA256.json`; los manifiestos y resultados de cierre-v1 son evidencia histórica del código probado. Dentro del ZIP, los informes originales permanecen bajo `entrega/` y el informe de esta actualización bajo `entrega/licencias-v1/`. Las nuevas comprobaciones son documentales y de integridad, no una repetición de la batería.

Estado al 26/10/2026: implementación local con batería reproducible y skill manual de solo lectura. La rúbrica y configuración siguen en 3.3.0; los ocho esquemas conservan sus identificadores v3.2–v3.4. Este cierre endurece validación de runtime y seguimiento: no se presenta como una extensión totalmente compatible con entradas antes aceptadas.

El Crítico ayuda a revisar supuestos de una propuesta antes de decidir. La evidencia, el juicio y la autorización humana siguen siendo necesarios. Un esquema válido no demuestra veracidad ni utilidad.

## Empezar por la skill

La carpeta `skills/critico/` contiene instrucciones y referencias autocontenidas. Su activación es manual y su trabajo es solo lectura: produce una revisión en el chat. No instala nada ni escribe registros. En Codex, la metadata incluye `allow_implicit_invocation: false`. La instalación en cualquier aplicación corresponde al encargado de destino.

Se separan cuatro capas: método universal, política Kuvexta opcional, contratos y CLI, e integración de destino. El prompt `prompts/critico_system.md` describe el contexto Kuvexta. No es obligatorio para una revisión universal.

## CLI y entorno local

Python >=3.10, PyYAML y jsonschema son dependencias del modo asistido; pytest está declarado para futuras suites. La ejecución de esta entrega se acredita en Python 3.14.7 Windows, con versiones exactas en `entrega/cierre-v1/DEPENDENCIAS.txt`. No se acredita una matriz de plataformas.

En esta carpeta se preparó un entorno aislado. En PowerShell:

```powershell
& .\.entorno-cierre\venv\Scripts\python.exe -B -X utf8 probar_todo.py
```

El entorno no se distribuye dentro del ZIP. Quien lo migre debe crear el suyo bajo sus reglas. Las dependencias y el código no se instalan globalmente mediante el paquete.

Ejemplo de flujo (usar el intérprete del entorno en lugar de `python`):

```text
python -B -X utf8 critico_cli.py triage --artefacto PROP-042 --perfil business
python -B -X utf8 critico_cli.py validar --triage triage-PROP-042.yaml --borrador
```

El generador entrega un **borrador**, no un triage operativo: completar fecha, dimensiones, conteos y referencias. `--borrador` comprueba estructura solamente; no comprueba fechas, marcadores ni reglas operativas. Las plantillas se entregan como borradores.

Tras completar triage, objeciones y veredicto:

```text
python -B -X utf8 critico_cli.py validar --triage triage-PROP-042.yaml --objecion objection.yaml --verdict verdict.yaml
python -B -X utf8 critico_cli.py verificar --triage triage-PROP-042.yaml --verdict verdict.yaml --artefacto propuesta.txt --bitacora veredictos.jsonl
python -B -X utf8 scripts/outcome_runner.py init --verdict verdict.yaml --objeciones objection.yaml --horizon corto_plazo
```

`verificar` exige un fichero de artefacto y una bitácora existente (puede estar vacía cuando no hay reset). Para M3 busca una suspensión única, válida, del artefacto correcto; exige preguntas resueltas y hash actual distinto del registrado. El hash histórico declarado no es una firma ni una certificación de la bitácora.

El outcome inicial también es un borrador. Completar fecha, evidencia y procedencia antes de:

```text
python -B -X utf8 scripts/outcome_runner.py validar --outcome outcome-PROP-042.yaml
python -B -X utf8 scripts/outcome_runner.py metricas --bitacora outcomes.jsonl --by profile
```

Las métricas rechazan registros inválidos antes de calcular. Intervenciones se agrupan por `verdict_id`; null/ausente significa no informado. Varios horizontes pueden aportar varias observaciones: las métricas de predicción siguen siendo por observación, mientras intervención es por decisión. No se infiere causalidad.

## Contratos y límites

- `validar`: esquema, fechas operativas, marcadores y reglas locales. No equivale a `verificar` para M3.
- `verificar`: coherencia triage/veredicto y evidencia de reset; cualquier registro histórico inválido se rechaza. Duplicados de suspensión requieren desambiguación fuera de esta herramienta.
- Seguimiento: `completo` y `omitidos` deben concordar. La omisión deliberada se conserva como seguimiento parcial.
- Evidencia: HASH_VERIFICADO significa correspondencia de contenido. Remoto, inaccesible o sin hash se indican NO_VERIFICADO. Solo el desacuerdo de hash rechaza en esta comprobación. Las rutas relativas de evidencia y de `validar --artefacto` parten de la carpeta del documento. `verificar --artefacto` usa la ruta del comando.
- Fechas: se exige fecha/hora con zona y calendario válido. No hay todavía política automática de vigencia, reputación de fuentes ni autenticación de bitácoras.
- Migración: esquema real obligatorio, cuarentena visible, revalidación de registros ya migrados y preservación de entrada. No ejecutar migraciones sobre datos reales sin el encargo correspondiente.

## Evidencia de cierre

La batería distingue aprobadas, fallidas y no comprobables y devuelve código 1 ante fallo o limpieza incompleta. Escribe únicamente temporales propios bajo `_tmp_pruebas/run-…`, dirige allí los temporales de subprocesos y desactiva bytecode. No limpia cachés previos ni el padre de temporales. Los comandos de CLI que crean artefactos sí escriben en sus destinos explícitos: la condición de solo lectura pertenece a la skill.

Resultados exactos y fuentes ensayadas: `entrega/cierre-v1/RESULTADOS.json`. Cobertura: `MATRIZ_COBERTURA.csv`. El piloto es sintético, no valida decisiones reales ni utilidad en producción. La revisión y las pruebas de este lote fueron realizadas por el mismo agente implementador; no son ratificación independiente.

Los 153 tests históricos siguen sin materializarse. `07_Makefile` y `08_critico-ci.yml` son referencias históricas; no representan CI activa. Las 34 invariantes del diseño no se declaran íntegramente acreditadas por esta batería.

Los incidentes y autorizaciones históricos conservan su estado; este cierre técnico no los resuelve retroactivamente. La migración a Kuvexta, el registro BZ, P01, check_encargo y P22 corresponden al encargado de destino. No se accedió al workspace para realizar este lote.

## Entrega bilingüe — 27/10/2026

[English](docs/en/README.md) · [Idiomas y contratos estables](docs/LANGUAGES.md) · [Compatibilidad de API](docs/API_COMPATIBILITY.md).

El lote BILINGUE-CRITICO-01 incorpora código interno inglés e interfaces heredadas compatibles, mensajes EN/ES, documentación y una sola skill bilingüe. El paquete de esta entrega es entrega/bilingue-v1/critico-bilingual-v1.zip; consultar REPORT.es.md, RESULTS.json, COVERAGE.csv y MANIFEST_SHA256.json de esa carpeta para su estado final. Los paquetes mencionados arriba son entregas anteriores y se conservan.

Usar --lang en|es, con prioridad sobre CRITIC_LANG; sin selección se mantiene español. Las pruebas usan temporales propios _tmp_pruebas/run-bilingual-<pid>-<uuid>/. No se traducen claves de contrato, enums ni evidencia aportada por el usuario. Autor y estado de licencia no cambian.

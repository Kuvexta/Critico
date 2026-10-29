# CHANGELOG

## 00.02.04 — 2026-10-29 — Suite histórica de 153 tests MATERIALIZADA (+ GATE B espejo)

- `tests/` materializado: 15 archivos, 153 tests (8+5+4+10+5+10+15+12+23+11+20+4+5+5+16), reconstruidos desde la especificación del manual §12.1 (invariantes M1/M2/M3, R1/R2/R4, G1/G1-bis/G2, I1/I2/I3, M-A…M-F y harness §13–14). El anexo histórico no era recuperable de los paquetes (verificado en cierre-v1/v2 y bilingue-v1) — reconstrucción fiel a la especificación, declarada en la adenda del manual.
- Módulos materializados: `evals/comparator.py` (métricas globales + por-dimensión + detección de regresión), `evals/html_report.py` (panel self-contained, WCAG AA, sección de skips M-E), `evals/history.py` + `evals/html_history.py` (store, tendencias, sparklines, skip_incident_rate con flecha invertida M-F), `scripts/render_eval_history.py`, `baseline/v3.4.0.json`, `history/manifest.yaml`, `tests/requirements.txt`.
- Regla R4 en `evals/risk_rules.py` (NO congelado — `evals/validators.py` congelado por CAMBIO-16 queda INTACTO, freeze OK). Su cableado al pipeline `validate_record` es candidata de CAMBIO (backlog).
- Verificación: `make test` 153 passed · batería `probar_todo.py` 100/100 · `make verify-freeze` OK v3.4.0 · CI ampliado con la suite.
- Kit de gobernanza leído (2026-10-29, P22). Autorización: literal de Dirección «suite 153 + GATE B» (2026-10-29).

 — Crítico (sistema + documentos + carpeta)

> Formato: por fecha. Sistema v3.4.0 congelado; documento manual v1.0.0; diseño universal v1.1.0.
> Repositorio público desde REPO-CRITICO-02 (2026-10-28); las rutas `registros/…` citadas abajo apuntan al archivo privado de gobernanza.

## 00.02.03+audit — 2026-10-28 — AUDIT-CRI-01: honestidad documental y limpieza de producción

- `09_golden_set/README.md`: declara lo pendiente (baseline solo v3.3.0; maquinaria no materializada) — sin promesas no demostradas.
- `07_Makefile`: cabecera v3.4; targets test/eval marcados historicos.
- `02_FROZEN_v3.4.md` §8: puntero al flujo canonico (CONTRIBUTING + Ecosistema MUTACIONES); el procedimiento numerado queda historico.
- `CONTRIBUTING.md`: referencia correcta del reconciliador (Kuvexta/Ecosistema).
- `README.md`: nota de scripts historicos.
- Limpieza de produccion con acta (registros_privados): borrados 08_critico-ci.yml (acciones sin fijar) y _freeze_migracion.log (v3.3.0); conservada entrega/.
- Autorizacion: `OK 34d59a62` (AUDIT-CRI-01, auditoria espejo 2026-10-28).

## 00.02.03+ecosistema — 2026-10-28 — El know-how operativo pasa a Kuvexta/Ecosistema

- Nuevo repo publico **Kuvexta/Ecosistema** (00.01.00): playbooks (mutaciones, GATE B espejo, publicacion, respaldo, limpieza, replicacion), herramientas (reconciliador canonico con config por estacion, instalador systemd), unidades del loop y plantillas.
- `scripts/sincronizar_copias.py` de este repo queda como puntero a la copia canonica (sin borrar: los borrados los hace Andres).
- AGENTS.md apunta al nuevo repo; el timer systemd de la estacion ya usa la copia canonica.
- Autorizacion: orden directa de Andres («organizar el know-how para replicar el ecosistema», 2026-10-28).

## 00.02.03+gitops — 2026-10-28 — Reconciliación automática (GitOps en miniatura)

- `scripts/sincronizar_copias.py` ampliado a reconciliador completo: `--pull` (git fetch + merge --ff-only, nunca reescribe historia), `--log` (bitacora JSONL), `--bup` (espejo curado de BUP en D:\, incluidos docs/diseno e INSTALACION) y salida de ciclo sano.
- Automatizado con systemd: `kuvexta-reconciliar.timer` (cada 10 min, Persistent) + servicio oneshot, linger activado; primer ciclo en verde (corrigio su propia deriva y completo INSTALACION.md y diseno/HASHES.md en el espejo BUP).
- Metodologia documentada en AGENTS.md (principios OpenGitOps: declarativo, versionado, pull automatico, reconciliacion continua) + CI de GitHub como segunda red.
- Autorizacion: orden directa de Andres («investiga como se hace con sistemas agenticos y automatiza los espejos», 2026-10-28).

## 00.02.03+sync — 2026-10-28 — Herramienta de sincronización de copias

- `scripts/sincronizar_copias.py`: sincroniza producción y workspace desde el clon del repo (dry-run por defecto; copia solo lo rastreado por git, compara por SHA-256, no borra nada). Evita la deriva que dejó 37 archivos desincronizados en producción.
- AGENTS.md y CONTRIBUTING.md documentan su uso en cada CAMBIO.
- Autorizacion: orden directa de Andres («que mas te falta organizar ya que no tenia nada sincronizado», 2026-10-28).

## 00.02.03+github — 2026-10-28 — Proceso de interacción en GitHub mejorado

- Plantillas de issues (propuesta CAMBIO estructurada, reporte de error, pregunta) y PR; `SECURITY.md` para reporte privado de vulnerabilidades.
- CI real: `.github/workflows/critico-ci.yml` (bateria + freeze + guarda en cada push y PR); retirado el `08_critico-ci.yml` obsoleto (rutas v3.3).
- Etiquetas de clasificacion y flujo de aceptacion documentado en CONTRIBUTING (comentario de cierre con CAMBIO id y SHA; registro en el archivo privado).
- Autorizacion: orden directa de Andres («Que consideras que lo podamos mejorar mas ese proceso de interacion en github», 2026-10-28).

## 00.02.03+contribucion — 2026-10-28 — CONTRIBUTING.md: cómo aportar desde cualquier plataforma

- `CONTRIBUTING.md` nuevo: mapa de archivos (qué se actualiza dónde, congelado sí/no), flujo de propuesta CAMBIO («OK <8hex>»), ejemplo de sub-perfil y limites honestos.
- `AGENTS.md`: seccion «Si quieres mejorar el Critico»; README: enlace a CONTRIBUTING.
- Autorizacion: orden directa de Andres («que el agente de cualquier plataforma sepa donde se actualiza y como mejorar el Critico», 2026-10-28).

## 00.02.03+estructura — 2026-10-28 — Orientación para agentes y estructura del repo

- `AGENTS.md` nuevo: orientación para cualquier agente (entrada rápida, reglas de solo lectura, instalación por plataforma).
- `skills/critico/` actualizada a la versión de la entrega (cláusula de seguridad: «solo tras solicitud explícita del usuario» y autoría).
- `LEEME.md` reescrito como puntero al README canónico; `README_PRODUCTO.md` con nota de documento histórico (sus rutas entrega/ y licencias/ viven en el archivo privado).
- README: advertencia de instalar una sola variante y enlace a AGENTS.md.
- Autorizacion: orden directa de Andres («revisar si cualquier agente no se pierda que todo este bien estructurado», 2026-10-28).

## 00.02.03+plataformas — 2026-10-28 — Variantes de skill para las 12 plataformas + universal

- `plataformas/` incorpora las 13 variantes de la entrega skills-cli-ide-v1 (manifiesto SHA-256 3b0a0e3e…): opencode, claude-code, cursor, codex, cline, gemini-cli, github-copilot, kiro, openclaw, qwen-code, deepseek-harness, antigravity y universal; cada una con README (ruta exacta), LICENSE y AUTORIA.
- README: tabla de plataformas con destinos de instalacion.
- Autorizacion: orden directa de Andres («el dice skill para opencode pero debe mencionar a todos los que hicimos para cada plataforma», 2026-10-28).

## 00.02.03+readme — 2026-10-28 — README ampliado para la comunidad

- Qué es (GATE B, objeciones falsables, steelman, veredicto, outcomes), requisitos (Python >=3.10), flujo GATE B en 6 pasos, CLI completo, dimensiones/perfiles, limites honestos y repos hermanos.
- Correcciones: la tabla de estructura ya no lista `registros/` (fuera del repo publico) y la regla cita la frase canonica corregida «OK <8hex>» (sin «OK-escribir»).
- Autorizacion: orden directa de Andres («Actualizar todas las documentaciones y repositorios y sincronizar o coordinar lo que consideres», 2026-10-28).

## 00.02.03+repo — 2026-10-28 — REPO-CRITICO-02: repositorio publicado a la comunidad

- Kuvexta/Critico pasa a **publico** (decision de Andres): codigo MIT, documentacion CC BY-SA 4.0, etapa construccion 00.02.03 declarada como beta honesto.
- Historia nueva sin `registros/` (borrar+recrear, patron del protocolo de cero reescritura); respaldo del historial privado conservado fuera del repositorio.
- Correccion de textos obsoletos del README (02_FROZEN_v3.4, mapeo 3.4.0) y seccion «Comunidad».
- Comandos slash para la comunidad: `commands/` con 14 alias — `/ojocritico` (principal), `/ojo-critico`, `/critico`, `/gateb`, `/premortem`, `/punto-ciego`, `/revision-critica`, `/devils-advocate`, `/challenge-review`, `/critical-eye`, `/steelman`, `/falsabilidad`, `/falsifiability` y `/argumento-de-acero` (la skill mantiene el id `critico`).
- Autorizacion: orden directa de Andres (respuestas «Publico sin registros/» y «Si, como beta honesto», 2026-10-28).

## 00.02.03 — 2026-10-28 — CAMBIO-16: el freeze ancla el SHA-256 de evals/validators.py

- `scripts/verify_freeze.py`: comprueba que `evals/validators.py` coincide con el SHA-256 congelado (26471259…, estado tras CAMBIO-15); el mensaje de exito pasa a «… · reglas locales congeladas · …». Cierra la leccion del CAMBIO-15: el freeze integral ahora cubre las reglas locales.
- Origen: leccion CAMBIO-15. Propuesta: registros/propuestas/CAMBIO-16.json.
- Autorizacion: orden directa de Andres (seleccion «CAMBIO-16 del Critico», 2026-10-28).
- Validacion: verify_freeze OK en las tres copias + caso de aceptacion (validators.py mutado → freeze exit 1 con la clave nueva; restaurado → exit 0) + bateria 99/0/1 (workspace y produccion) y 100/0/0 (repo).
- Sin cambios en rubrica, config (config_hash intacto), esquemas ni critic_version (3.4.0).

## 00.02.02 — 2026-10-28 — CAMBIO-15: el validador T1 admite las dimensiones 107 y 108

- `evals/validators.py`: la regex de active_dimensions pasa de 1..106 a 1..108 (los ids 109+ siguen rechazados con T1). CAMBIO-14 añadió las dimensiones 107/108 pero la regla local T1 no se actualizó; el mensaje T1 ya decía «entre 1 y 108».
- Origen: seis GATE B espejo independientes (campaña del diseño multiplataforma BUP v1.18) documentaron el rechazo. Propuesta: registros/propuestas/CAMBIO-15.json (SHA-256 821904b8…).
- Autorización: orden directa de Andrés («Realice lo que consideres», 2026-10-28).
- Validación: batería 99/0/1 (workspace y producción) y 100/0/0 (repo) + verify_freeze OK v3.4.0 en las tres copias + caso de aceptación: triage con 107/108 valida exit 0 y con 109 se rechaza (T1).
- Lección: el freeze integral cubre 8 esquemas + config + rúbrica, pero no las reglas locales de `evals/validators.py`; el desajuste 106/108 sobrevivió a CAMBIO-14 por esa vía. Candidato futuro: incluir el hash de `evals/validators.py` en el freeze.

## 00.02.01 — 2026-10-28 — Documentación actualizada a v3.4.0/108 dimensiones

- Manual (es/en), diseño universal (roadmap real), prompts, guías, golden set y cabeceras de changelog actualizados; la historia conserva «106» donde corresponde.

## 2026-10-27 — BILINGUE-CRITICO-01

- Implementación interna inglesa con alias y argumentos por nombre compatibles; nuevas entradas al mismo motor.
- Catálogos ES/EN, selección de idioma, ayuda y panel HTML traducidos; campos y decisiones de protocolo sin cambios.
- Documentación vigente, manual, diseño universal y una sola skill manual de solo lectura en ambos idiomas.
- Registro de hashes de traducción y paquete propio. RESULTS.json acredita los ensayos efectivamente realizados; no hay certificación independiente.

[English](docs/en/CHANGELOG.md).

## 2026-10-27 — AUTORIA-LICENCIAS-01

- Autor del proyecto identificado como KUVEXTA GROUP, sin atribuir materiales de terceros.
- Catálogo no activado: MIT, Apache-2.0, MPL-2.0, GPL-3.0-only, AGPL-3.0-only, CC BY y CC BY-SA 4.0; copias de referencia con URL, fecha y SHA-256.
- Borradores no vigentes de modelo propietario comercial, código visible y estrategia de doble licencia.
- Inventario de avisos de dependencias observadas en el entorno, sin relicenciarlas.
- Se conserva la declaración previa de LICENSE. La licencia futura y su aplicación requieren decisión aparte.
- Nuevo paquete con manifiesto propio; código funcional y entrega cierre-v1 conservados. Fuente: `entrega/licencias-v1/INFORME.md` y sus inventarios.

## 2026-10-26 — CIERRE-CRITICO-01 (versión asistida local)

- Validación compartida entre CLI, inicializador y métricas: fechas operativas, borradores explícitos, estados bidireccionales, conteos y seguimiento coherentes.
- M3 rechaza históricos inválidos y suspensiones ambiguas; compara la suspensión identificada con el hash actual calculado.
- Evidencias locales relativas al documento y manejo de inaccesibilidad; HASH_VERIFICADO acredita integridad, no veracidad.
- Migración con validación real obligatoria, idempotencia revalidada, entrada preservada y cuarentena. Patrones aceptan lista o contenedor.
- Batería distingue aprobadas/fallidas/no comprobables, reporta fallos de limpieza y usa temporales propios. Añade recorrido sintético y regresiones de contratos, migración y reporte.
- Skill manual de solo lectura y separación entre método, política, contratos e integración. Paquete con manifiesto SHA-256, inventarios, logs y matriz de cobertura.
- Entorno aislado autorizado por ENTORNO-CIERRE-01. Dependencias exactas y resultados en la entrega; no se instala ni migra al workspace.
- Las entradas anteriores son historia del proyecto. Sus cifras no son resultados actuales ni ratificación independiente. Los incidentes históricos permanecen pendientes de decisión humana.

Fuente del cierre: código, `entrega/cierre-v1/RESULTADOS.json` y logs asociados del 26/10/2026. Cualquier resultado posterior debe indicar sus propios hashes de fuentes.

## 2026-10-26 — Nacimiento y consolidación

### Sistema (v2.0 → v3.3.0)
- v2.0: 11 ángulos, diseño inicial · v3.0: C1–C6 + U1–U4 (106 dimensiones) · v3.1: B1–B4 + R1–R5 + M1–M3 · v3.2: enforcement G1/G1-bis/G2 · v3.3: integración I1–I3 + M-A a M-F (153 tests diseñados).
- Esquemas: objection, triage, verdict, risk_accepted, skip_incident (v3.3); golden_case (v3.3); outcome, pattern (v3.4).

### Documentos de la carpeta
- `01_Manual_completo_del_Critico_v1.0.0.md` — consolidación del fuente roto (12.282 líneas, 13 entregas) a manual profesional.
- `02_FROZEN_v3.3.md` — acta de congelación (34 invariantes).
- `13_Diseno_Completo_Universal_Critico.md` v1.0.0 → **v1.1.0**: bucle de mejora (§15), multi sub-perfil (§7.5), 20 macro-perfiles y 164→**153 sub-perfiles** tras la auditoría de fusiones (§7.6).
- `14_AUDITORIA_FINAL.md` — ronda 1 (9 correcciones) + ronda 2 (fusiones).
- `16_GATE_B_Autoauditoria.md` — auto-GATE B del producto: **PASA_CON_CONDICIONES** con 6 condiciones.

### Herramientas (modo asistido)
- `critico_cli.py`, `prompts/critico_system.md`, `templates/` (7), `README_PRODUCTO.md`, `probar_todo.py` (PASS 17/17).
- Bucle: `scripts/outcome_runner.py`, `evals/calibration.py`, `evals/patterns.py`, `evals/calibration_panel.py`, `scripts/autopopulate_v1_angle.py`.

### Correcciones notables
- Escapes `\_` residuales (bug del conversor) · monólogo interno eliminado del anexo · enum YAML 1.1 `no`→False (outcome/pattern) · f-string 3.12 → compatible 3.10 · conteo de esquemas 9→8.

### Ronda 3 — Revisión independiente (verificador externo)
- 8 hallazgos aceptados y corregidos: contrato veredicto→outcome · validadores unificados (M1/M2/M3/I3/G5/X1) · `required` en I3 · protección de escrituras (4 herramientas) · migración con JSON Schema real · perfiles de extensión bloqueados en triage · prompt corregido (RIESGO_NO_EVALUADO terminal) · actas honestas sobre la suite.
- `probar_todo.py` con casos negativos → **PASS 31/31**.

### Ronda 4 — Segunda revisión independiente
- 4 huecos corregidos: prueba de campo AUSENTE (del key) · `verificar` valida esquemas primero · M3 profunda (preguntas resueltas + cambio de hash demostrable) · inicializador RECHAZA objeciones incompatibles (`--ignorar-incompatibles` opcional).
- `probar_todo.py` → PASS 37/37 (con casos negativos rondas 1–4). README matiza: el validador NO es garantía técnica hasta acreditar la suite.

### Pendiente
- Ejecutar los 153 tests (materializar repo) · decisiones de Dirección (§4 de la auditoría).

# API compatibility / Compatibilidad de API
KUVEXTA GROUP · 2026-10-27

English implementation names are canonical; existing Spanish entry points, keyword arguments and exception identities remain available. English and Spanish commands use the same engine. / Los nombres internos ingleses son canónicos; se mantienen las entradas, argumentos por nombre y excepciones anteriores. Ambos idiomas usan el mismo motor.

| Existing / Existente | English alias |
| --- | --- |
| critico_cli.py | critic_cli.py |
| probar_todo.py | run_tests.py |
| validar | validate |
| verificar | verify |
| plantilla | template |
| angulos | angles |
| perfiles | profiles |
| --artefacto | --artifact |
| --borrador | --draft |
| --bitacora | --log |
| --archivo | --file |
| --tipo | --type |
| --perfil | --profile |
| --permitir-extension | --allow-extension |
| --objecion | --objection |
| --riesgo | --risk |
| --patron | --pattern |
| outcome_runner: metricas | metrics |
| outcome_runner: expirados | expired |
| --objeciones | --objections |
| --ignorar-incompatibles | --ignore-incompatible |
| --riesgos | --risks |
| --hoy | --today |

Language / idioma: --lang en|es > CRITIC_LANG > es. Invalid preferences produce a visible bilingual warning and fall back to es. Missing translation keys are errors, not silent fallback. / Preferencias inválidas avisan y usan es; claves ausentes son errores.

Data contracts are unchanged: YAML/JSON keys, enum values, identifiers, hashes, output filenames, rule codes, return codes and formulas. RESULTADOS_JSON keeps the same keys (aprobadas, fallidas, no_comprobables, total, casos); since R-FIX-07 the `casos` value is a list of objects {nombre, estado, detalle} with textual estado aprobada|fallida|no comprobable instead of tuples with True/False/None. Only owned human guidance may differ; outcome comparisons normalize those guidance fields. Dependency diagnostics, fixture inputs, canonical wire strings, historical references and legacy API names are deliberate exceptions to English internal text. / Los contratos no cambian; los datos externos y nombres de compatibilidad no se traducen. RESULTADOS_JSON conserva las mismas claves (aprobadas, fallidas, no_comprobables, total, casos); desde R-FIX-07 el valor de `casos` es una lista de objetos {nombre, estado, detalle} con estado textual aprobada|fallida|no comprobable, en lugar de tuplas con True/False/None.

ReglaViolada and RuleViolation are the same exception class. The table below records compatibility wrappers and their exact signatures from the implementation. / Ambas excepciones son la misma clase; la tabla registra firmas de compatibilidad.

| Module | Legacy wrapper / Firma anterior | Delegated function / Función |
| --- | --- | --- |
| critico_cli.py | `print_angles()` | `print` |
| critico_cli.py | `cargar_esquema(nombre: str)` | `load_schema` |
| critico_cli.py | `validar(nombre: str, path: str, artefacto_ruta: str | None=None, borrador: bool=False)` | `validate` |
| critico_cli.py | `plantilla(tipo: str, out: str | None, force: bool=False)` | `copy_template` |
| critico_cli.py | `generar_triage(artefacto: str, perfil: str, sub: str | None, secondary: list[str], permitir_extension: bool=False)` | `generate_triage` |
| critico_cli.py | `cmd_angulos()` | `print_angles` |
| critico_cli.py | `cmd_perfiles()` | `print_profiles` |
| critico_cli.py | `cmd_v1angle(objecion: str, in_place: bool)` | `derive_angle` |
| critico_cli.py | `cmd_verificar(triage_file: str, verdict_file: str, artefacto: str, bitacora: str)` | `verify_consistency` |
| critico_cli.py | `cmd_hash(archivo: str)` | `print_hash` |
| critico_cli.py | `verificar_evidencias(rec: dict, artefacto_ruta: str | None, documento_dir: Path | None=None)` | `verify_evidence` |
| probar_todo.py | `reject_links(path: Path)` | `OSError` |
| probar_todo.py | `paso(nombre: str, ok: bool | None, detalle: str='')` | `step` |
| probar_todo.py | `paso_neg(nombre: str, r: subprocess.CompletedProcess, codigo: str)` | `expect_rejection` |
| probar_todo.py | `tmp_autorizado()` | `owned_temporary_directory` |
| probar_todo.py | `sin_enlaces(path: Path)` | `reject_links` |
| probar_todo.py | `limpiar_propio(path: Path)` | `clean_owned` |
| probar_todo.py | `base_objeccion(oid: str, dims: list[str], artifact: str='PROP-PRUEBA-001', hash_artefacto: str='abc')` | `make_objection` |
| probar_todo.py | `base_verdict(status: str='PASA_CON_CONDICIONES', reason_code=None, con_trail: bool=True)` | `make_verdict` |
| probar_todo.py | `base_triage(artifact: str='PROP-PRUEBA-001', preguntas_resueltas: bool=True, union_raw: int=5, overrides: list | None=None)` | `make_triage` |
| probar_todo.py | `_main_interna()` | `run_legacy_cases` |
| probar_todo.py | `_pruebas_cierre()` | `run_closure_cases` |
| evals/validators.py | `_fail(msg: str)` | `RuleViolation` |
| evals/validators.py | `require_rules(rules: list[str], context: str)` | `RuleViolation` |
| evals/validators.py | `validar_registro(tipo: str, rec: dict, borrador: bool=False)` | `validate_record` |
| evals/validators.py | `validar_coherencia(triage: dict, verdict: dict, hash_actual: str | None=None, hash_suspension: str | None=None, suspension_encontrada: bool=False)` | `validate_coherence` |
| evals/validators.py | `exigir(reglas: list[str], contexto: str)` | `require_rules` |
| evals/calibration.py | `_outcome_bool(outcome: str)` | `ValueError` |
| evals/calibration_panel.py | `_estado(sobre: float)` | `_status` |
| evals/calibration_panel.py | `_celda(texto: str, color: str | None=None)` | `_cell` |
| scripts/outcome_runner.py | `cmd_init(verdict_file: str, horizon: str, objeciones_files: list[str], ignorar_incompatibles: bool=False)` | `initialize_outcome` |
| scripts/outcome_runner.py | `cmd_validar(outcome_file: str)` | `validate_outcome` |
| scripts/outcome_runner.py | `cmd_metricas(bitacora: str, by: str | None)` | `print_metrics` |
| scripts/outcome_runner.py | `cmd_expirados(riesgos: str, hoy: str | None)` | `print_expired` |
| 06_migration/v2_to_v3.py | `validate_objection(rec: dict)` | `validar_registro` |

Acceptance evidence / Evidencia: entrega/bilingue-v1/RESULTS.json and COVERAGE.csv. Test success covers exercised contracts, not every possible downstream consumer. / Las pruebas cubren contratos ensayados, no todos los consumidores posibles.

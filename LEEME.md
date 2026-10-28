# El Crítico — entrada a la entrega local

Fecha de referencia: 26/10/2026.

1. Leer `README_PRODUCTO.md` para uso y límites actuales.
2. Usar `skills/critico/SKILL.md` para revisión manual de solo lectura.
3. Consultar `entrega/cierre-v1/CIERRE.md` y `RESULTADOS.json` para estado verificado, incidencias y pendientes.
4. Entregar `entrega/cierre-v1/critico-cierre-v1.zip` al encargado de migración junto con su SHA-256.

## Mapa del paquete

- `critico_cli.py`, `evals/`, `scripts/` y `06_migration/`: herramientas locales.
- `03_rubric.yaml`, `04_critic.config.yaml`, `05_schema/`: rúbrica, configuración y ocho esquemas.
- `templates/`: siete borradores, que deben completarse para uso operativo.
- `skills/critico/`: método universal y referencia Kuvexta separada.
- `prompts/critico_system.md`: prompt contextual Kuvexta, sin permiso de ejecución ni escritura.
- Manual, freeze y diseño universal: referencias de diseño, no demostración de cobertura completa.
- `CHANGELOG.md` y `LECCIONES_APRENDIDAS.md`: historia y lecciones candidatas.
- `requirements.txt` y `LICENSE`: requisitos y licencia.

La carpeta de desarrollo conserva auditorías, propuestas y materiales históricos que no forman parte del ZIP. No confundir sus resultados antiguos con el estado de la entrega. El entorno `.entorno-cierre`, los cachés existentes y los temporales no se distribuyen.

## Verificación

Con el entorno ya preparado y autorización para crear/limpiar sus temporales:

```powershell
& .\.entorno-cierre\venv\Scripts\python.exe -B -X utf8 probar_todo.py
```

No usar `py_compile` para una inspección de solo lectura: genera bytecode. La comprobación de sintaxis de este lote se hizo en memoria.

La incorporación al workspace la realiza su encargado. Este paquete no instala una skill, no activa un plugin, no publica nada y no ejecuta CI remota.

## Entrega bilingüe — 27/10/2026

[English](docs/en/QUICKSTART.md) · [Índice de idiomas](docs/LANGUAGES.md).

La entrega actual prevista es entrega/bilingue-v1/critico-bilingual-v1.zip. Su informe, resultados y manifiesto propios determinan la aceptación; las rutas de cierre-v1 anteriores son históricas. critic_cli.py y run_tests.py son entradas inglesas al mismo motor. Usar --lang es o --lang en; la skill en español está en skills/critico/SKILL.es.md.

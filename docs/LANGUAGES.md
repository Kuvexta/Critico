# Languages / Idiomas

Date / Fecha: 2026-10-27. Author / Autor: **KUVEXTA GROUP**.

- [English product guide](en/README.md) · [Guía del producto en español](../README_PRODUCTO.md)
- [English quickstart](en/QUICKSTART.md) · [Entrada en español](../LEEME.md)
- [English manual](en/MANUAL.md) · [Manual original](../01_Manual_completo_del_Critico_v1.0.0.md)
- [English universal design](en/UNIVERSAL_DESIGN.md) · [Diseño original](../13_Diseno_Completo_Universal_Critico.md)
- [English schema guide](en/SCHEMA_GUIDE.md) · [Guía de esquemas](es/SCHEMA_GUIDE.md)
- [English skill](../skills/critico/SKILL.md) · [Skill en español](../skills/critico/SKILL.es.md)
- [English Kuvexta prompt](../prompts/critic_system.en.md) · [Prompt en español](../prompts/critico_system.md)
- [English license catalogue](en/licensing/README.md) · [Catálogo original](../licencias/README.md)
- [API compatibility](API_COMPATIBILITY.md) · [Source/translation registry](TRANSLATION_STATUS.json)

## Presentation language / Idioma de presentación

`--lang en|es` takes precedence over `CRITIC_LANG`. Without either, Spanish remains the default. The option works before or after a command. Invalid preferences produce a visible stderr warning and fall back to Spanish. Missing option values return exit code 2. Missing catalogue entries or mismatched placeholders fail acceptance; they do not silently fall back.

`--lang en|es` prevalece sobre `CRITIC_LANG`. Sin selección, se conserva español. La opción funciona antes o después del comando. Una preferencia inválida avisa en stderr y usa español; un valor ausente termina con código 2. Las traducciones ausentes o parámetros incompatibles impiden aprobar el lote.

```text
python -B -X utf8 critico_cli.py --lang en angles
python -B -X utf8 critico_cli.py angulos --lang es
python -B -X utf8 run_tests.py --lang en
python -B -X utf8 probar_todo.py --lang es
```

## Stable contracts / Contratos estables

JSON/YAML keys, enums, rule codes, evidence status tokens, canonical filenames and RESULTADOS_JSON keys remain unchanged. Spanish values such as `PASA`, `NO_PASA`, `si`, `parcial`, `desconocido`, `hecho` and `corto_plazo` are protocol data. Do not translate them. User evidence, quotations and original dependency diagnostics remain untouched. Only owned draft guidance may differ.

Las claves, enums, códigos, estados de evidencia, nombres canónicos y claves de RESULTADOS_JSON no cambian. Los datos del usuario, citas y diagnósticos originales de dependencias no se traducen. Solo puede variar la orientación humana de los borradores.

English implementations preserve Spanish public aliases and keyword wrappers. Test fixtures deliberately retain Spanish user data and legacy command arguments to exercise compatibility. Old global constants and test instrumentation hooks remain available. The language of these compatibility boundaries is not a second implementation.

Las implementaciones inglesas conservan alias y argumentos heredados; los fixtures mantienen datos españoles para probar compatibilidad. No hay un segundo motor.

## Translation authority / Autoridad de la traducción

The Spanish source documents remain the normative design references. English documents are translations dated 2026-10-27, identified with source and translation hashes. Historical counts, gates and plans remain historical; they do not certify current coverage. Original legal reference texts and third-party notices are unchanged. No future license has been activated.

Los originales españoles siguen como referencia normativa de diseño. Las traducciones se identifican con hashes. Las cifras históricas no acreditan cobertura actual. No se cambia ningún texto legal original ni se activa una licencia futura.

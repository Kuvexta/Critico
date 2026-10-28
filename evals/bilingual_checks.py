"""Additional bilingual acceptance checks; use the suite's confined fixtures."""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import contextlib
import hashlib
import inspect
import io
import json
import os
import subprocess

import yaml

import probar_todo as suite
from critic_i18n import get_language, load_catalog, set_language, translate, validate_catalogs

BASE = Path(__file__).resolve().parents[1]


def check(key: str, condition: bool, detail: str = "") -> None:
    suite.step(translate("checks." + key), condition, detail)


def invoke(entry: str, *arguments: str, language: str = "es", cwd: Path | None = None) -> subprocess.CompletedProcess:
    environment = dict(os.environ, CRITIC_LANG=language, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONNOUSERSITE="1")
    environment.pop("PYTHONPATH", None)
    for key in ("TMPDIR", "TEMP", "TMP"):
        environment[key] = str(suite.RAIZ_CORRIDA)
    return subprocess.run([sys.executable, "-B", "-X", "utf8", str(BASE / entry), *arguments],
                          cwd=cwd or BASE, env=environment, capture_output=True, text=True, encoding="utf-8")


def run_checks() -> None:
    check("catalogs", validate_catalogs() > 0)
    for language in ("en", "es"):
        check("catalog_nonempty", all(value.strip() for value in load_catalog(language).values()), language)

    import critico_cli as cli
    import critic_cli as english_cli
    from evals import validators, calibration
    from evals.calibration_panel import calibration_section, _estado, _celda
    from scripts import outcome_runner

    check("shared_engine", english_cli.main is cli.main)
    check("exception_identity", validators.ReglaViolada is validators.RuleViolation)
    check("legacy_keywords", list(inspect.signature(cli.validar).parameters) == ["nombre", "path", "artefacto_ruta", "borrador"]
          and list(inspect.signature(validators.validar_coherencia).parameters) == ["triage", "verdict", "hash_actual", "hash_suspension", "suspension_encontrada"]
          and list(inspect.signature(outcome_runner.cmd_init).parameters) == ["verdict_file", "horizon", "objeciones_files", "ignorar_incompatibles"])
    check("schema_alias", cli.cargar_esquema(nombre="verdict") == cli.load_schema(name="verdict"))
    verdict = suite.base_verdict(con_trail=True)
    triage = suite.base_triage(preguntas_resueltas=True)
    validators.validar_registro(tipo="verdict", rec=verdict, borrador=False)
    check("legacy_call", validators.validar_coherencia(triage=triage, verdict=verdict, hash_actual=None,
          hash_suspension=None, suspension_encontrada=False) == validators.validate_coherence(triage, verdict))
    check("helper_alias", _estado(sobre=0.05) == ("#1a7f37", "OK") and _celda(texto="safe", color=None) == "<td>safe</td>")

    for language, title in (("es", "Consola"), ("en", "console")):
        result = invoke("critic_cli.py", "--lang", language, "--help", language="en" if language == "es" else "es")
        check("cli_precedence", result.returncode == 0 and title in result.stdout, language)
        result = invoke("critic_cli.py", "angles", "--lang=" + language)
        check("lang_after_command", result.returncode == 0 and ("Costos" if language == "es" else "Costs") in result.stdout, language)
        original = invoke("critico_cli.py", "angulos", language=language)
        alias = invoke("critic_cli.py", "angles", language=language)
        check("command_alias", original.returncode == alias.returncode == 0 and original.stdout == alias.stdout, language)
        result = invoke("critic_cli.py", "validate", "--lang", language)
        check("localized_error", result.returncode == 2 and ("indica qué validar" if language == "es" else "specify what to validate") in result.stderr, language)
    invalid = invoke("critic_cli.py", "angles", language="invalid-language")
    check("visible_fallback", invalid.returncode == 0 and "unsupported language" in invalid.stderr and "Costos" in invalid.stdout)
    invalid = invoke("critic_cli.py", "--lang", "unknown", "angles", language="en")
    check("invalid_cli_fallback", invalid.returncode == 0 and "unsupported language" in invalid.stderr and "Costos" in invalid.stdout)
    missing = invoke("critic_cli.py", "--lang")
    check("missing_lang", missing.returncode == 2 and "--lang requires" in missing.stderr)

    with suite.owned_temporary_directory() as directory:
        artifact = directory / "Costos Seguridad evidencia.txt"
        artifact.write_text("Datos del usuario: no traducir. User data: do not translate.", encoding="utf-8")
        original_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
        objection = suite.base_objeccion("OBJ-111111111111", ["1"], hash_artefacto=original_hash)
        objection["evidence_detail"] = [{"source": artifact.name, "accessed_at": "2026-10-27T00:00:00Z", "kind": "hecho", "hash": original_hash}]
        objection_path = directory / "objection.yaml"
        objection_path.write_text(yaml.safe_dump(objection, allow_unicode=True), encoding="utf-8")
        verdict_path = directory / "verdict.yaml"
        verdict_path.write_text(yaml.safe_dump(verdict), encoding="utf-8")
        generated = []
        for language in ("es", "en"):
            result = invoke("critic_cli.py", "validate", "--objection", str(objection_path), "--artifact", artifact.name, language=language)
            check("evidence_preserved", result.returncode == 0 and artifact.name in result.stdout and result.stdout.count("HASH_VERIFICADO") == 2, language)
            result = invoke("critic_cli.py", "hash", "--file", str(artifact), language=language)
            check("hash_invariant", result.returncode == 0 and result.stdout.split()[0] == original_hash, language)
            target = directory / language
            target.mkdir()
            result = invoke("scripts/outcome_runner.py", "init", "--verdict", str(verdict_path), "--objections", str(objection_path), language=language, cwd=target)
            check("outcome_alias", result.returncode == 0, result.stderr)
            record = yaml.safe_load((target / "outcome-PROP-PRUEBA-001.yaml").read_text(encoding="utf-8"))
            # Only owned draft guidance is allowed to differ across languages.
            record["provenance"]["model_version"] = "<GUIDANCE>"
            for item in record["objection_outcomes"]:
                item["evidence"] = "<GUIDANCE>"
            generated.append(record)
        check("normalized_records", generated[0] == generated[1])
        check("input_unchanged", hashlib.sha256(artifact.read_bytes()).hexdigest() == original_hash
              and yaml.safe_load(objection_path.read_text(encoding="utf-8")) == objection)

    selected = get_language()
    outputs = []
    for language in ("es", "en"):
        set_language(language)
        records = [{"verdict_id": "V1", "objection_outcomes": [{"materialized": "no", "mitigacion_aplicada": True, "propuesta_cancelada": False}]}]
        outputs.append(calibration.intervention_metrics(rows=records))
        check("metrics_alias", calibration.metricas_intervencion(rows=records) == outputs[-1], language)
        profile = "<script>alert('Costos')</script>&"
        values = {profile: {"n": 1, "brier": 0.04, "mean_confidence": 0.2, "observed_rate": 0.0, "overconfidence": 0.2}}
        html = calibration_section(values, [])
        check("html_escape", "<script>" not in html and "&lt;script&gt;" in html and "&amp;" in html, language)
        check("html_language", ("Calibración de confianza" if language == "es" else "Confidence calibration") in html, language)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            cli.verificar_evidencias(rec={"evidence_detail": [{"source": "https://example.invalid/Costos", "hash": "a" * 64}]}, artefacto_ruta=None, documento_dir=BASE)
        check("remote_unchanged", "https://example.invalid/Costos" in stream.getvalue() and "NO_VERIFICADO(remoto)" in stream.getvalue(), language)
    set_language(selected)
    check("metrics_invariant", outputs[0] == outputs[1] and outputs[0]["intervencion_rate"] == 1.0)

    from scripts.package_bilingual import document_checks
    for name, passed, detail in document_checks():
        check("documents", passed, name + (": " + detail if detail else ""))

    import critic_i18n
    try:
        translate("missing.acceptance.key")
    except KeyError:
        missing_key_rejected = True
    else:
        missing_key_rejected = False
    check("missing_translation", missing_key_rejected)
    original_loader = critic_i18n.load_catalog
    try:
        critic_i18n.load_catalog = lambda language: {"probe": "{value}" if language == "en" else "{other}"}
        try:
            critic_i18n.validate_catalogs()
        except ValueError as error:
            mismatch_rejected = "placeholders differ" in str(error)
        else:
            mismatch_rejected = False
    finally:
        critic_i18n.load_catalog = original_loader
    check("placeholder_negative", mismatch_rejected)



if __name__ == "__main__":
    suite._main_interna = run_checks
    suite._pruebas_cierre = lambda: None
    suite.main()

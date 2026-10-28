"""Build this authorized delivery from tested sources; --check is read-only.

A fresh build requires the development proposal and inventory. Distributed users
can run --check; rebuilding must use their own explicitly authorized baseline.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import ast
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

import yaml

BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "entrega/bilingue-v1"
PRODUCT_FILES = ['01_Manual_completo_del_Critico_v1.0.0.md', '02_FROZEN_v3.3.md', '03_rubric.yaml', '04_critic.config.yaml', '05_schema/golden_case.yaml', '05_schema/objection.yaml', '05_schema/outcome.yaml', '05_schema/pattern.yaml', '05_schema/risk_accepted.yaml', '05_schema/skip_incident.yaml', '05_schema/triage.yaml', '05_schema/verdict.yaml', '06_migration/v2_to_v3.py', '13_Diseno_Completo_Universal_Critico.md', 'AUTORIA.md', 'CHANGELOG.md', 'LECCIONES_APRENDIDAS.md', 'LEEME.md', 'LICENSE', 'README_PRODUCTO.md', 'critic_cli.py', 'critic_i18n.py', 'critico_cli.py', 'docs/API_COMPATIBILITY.md', 'docs/LANGUAGES.md', 'docs/TRANSLATION_STATUS.json', 'docs/en/AUTHORSHIP.md', 'docs/en/CHANGELOG.md', 'docs/en/LESSONS_LEARNED.md', 'docs/en/MANUAL.md', 'docs/en/QUICKSTART.md', 'docs/en/README.md', 'docs/en/SCHEMA_GUIDE.md', 'docs/en/UNIVERSAL_DESIGN.md', 'docs/en/licensing/COMPARISON.csv', 'docs/en/licensing/DUAL-LICENSING.draft.md', 'docs/en/licensing/PROPRIETARY-COMMERCIAL.draft.md', 'docs/en/licensing/README.md', 'docs/en/licensing/SOURCE-AVAILABLE.draft.md', 'docs/en/licensing/THIRD_PARTY_NOTICES.md', 'docs/es/SCHEMA_GUIDE.md', 'evals/bilingual_checks.py', 'evals/calibration.py', 'evals/calibration_panel.py', 'evals/patterns.py', 'evals/validators.py', 'licencias/COMPARATIVA.csv', 'licencias/DECISION_PENDIENTE.json', 'licencias/DOBLE-LICENCIA.borrador.md', 'licencias/PROPIETARIA-COMERCIAL.borrador.md', 'licencias/README.md', 'licencias/SOURCE-AVAILABLE.borrador.md', 'licencias/TERCEROS.md', 'licencias/referencia/AGPL-3.0-only.txt', 'licencias/referencia/Apache-2.0.txt', 'licencias/referencia/CC-BY-4.0.txt', 'licencias/referencia/CC-BY-SA-4.0.txt', 'licencias/referencia/GPL-3.0-only.txt', 'licencias/referencia/MIT.txt', 'licencias/referencia/MPL-2.0.txt', 'locales/en.json', 'locales/es.json', 'probar_todo.py', 'prompts/critic_system.en.md', 'prompts/critico_system.md', 'requirements.txt', 'run_tests.py', 'scripts/autopopulate_v1_angle.py', 'scripts/outcome_runner.py', 'scripts/package_bilingual.py', 'scripts/verify_freeze.py', 'skills/critico/SKILL.es.md', 'skills/critico/SKILL.md', 'skills/critico/agents/openai.yaml', 'skills/critico/references/en/kuvexta.md', 'skills/critico/references/en/method.md', 'skills/critico/references/en/output-format.md', 'skills/critico/references/formato-salida.md', 'skills/critico/references/kuvexta.md', 'skills/critico/references/metodo.md', 'templates/objection.yaml', 'templates/outcome.yaml', 'templates/pattern.yaml', 'templates/risk_accepted.yaml', 'templates/skip_incident.yaml', 'templates/triage.yaml', 'templates/verdict.yaml']


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def document_checks() -> list[tuple[str, bool, str]]:
    """Check actual files, structure and metadata without writing or executing code."""
    checks = []
    def record(name, condition, detail=""):
        checks.append((name, bool(condition), detail))
    registry = read_json(BASE / "docs/TRANSLATION_STATUS.json")
    for item in registry["records"]:
        record("translation:" + item["translation"],
               digest(BASE / item["source"]) == item["source_sha256"]
               and digest(BASE / item["translation"]) == item["translation_sha256"],
               item["source"])
    for source, target, extra_heading in (
        ("01_Manual_completo_del_Critico_v1.0.0.md", "docs/en/MANUAL.md", 0),
        ("13_Diseno_Completo_Universal_Critico.md", "docs/en/UNIVERSAL_DESIGN.md", 1),
    ):
        original, translated = [(BASE / p).read_text(encoding="utf-8") for p in (source, target)]
        def counts(text):
            return (len(re.findall(r"(?m)^#{1,6} ", text)),
                    sum(line.startswith("|") for line in text.splitlines()),
                    len(re.findall(r"(?m)^" + chr(96)*3, text)))
        a, b = counts(original), counts(translated)
        record("structure:" + target, b == (a[0]+extra_heading, a[1], a[2]), f"{a} -> {b}")
        def dimension_ids(text):
            return re.findall(r"(?m)^\|\s*(\d+)\s*\|", text)
        record("numeric-table-ids:" + target, dimension_ids(original) == dimension_ids(translated))
    original = (BASE / "13_Diseno_Completo_Universal_Critico.md").read_text(encoding="utf-8")
    translated = (BASE / "docs/en/UNIVERSAL_DESIGN.md").read_text(encoding="utf-8")
    profile_pattern = r"(?m)^\|\s*`?([a-z_]+\.[a-z_]+)`?\s*\|"
    record("profile-identifiers", re.findall(profile_pattern, original) == re.findall(profile_pattern, translated))
    def legal_blocks(path):
        return re.findall(r"(?s)~~~~text\n(.*?)\n~~~~", path.read_text(encoding="utf-8"))
    original_blocks = legal_blocks(BASE / "licencias/TERCEROS.md")
    translated_blocks = legal_blocks(BASE / "docs/en/licensing/THIRD_PARTY_NOTICES.md")
    record("original-legal-notices", len(original_blocks) == 14 and original_blocks == translated_blocks)
    for name in ("skills/critico/SKILL.md", "skills/critico/SKILL.es.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", text, re.S)
        metadata = yaml.safe_load(match.group(1)) if match else {}
        record("skill-frontmatter:" + name, metadata.get("name") == "critico"
               and isinstance(metadata.get("description"), str)
               and 0 < len(metadata["description"]) <= 1024
               and set(metadata) <= {"name", "description", "license", "allowed-tools", "metadata"})
    metadata = yaml.safe_load((BASE / "skills/critico/agents/openai.yaml").read_text(encoding="utf-8"))
    record("skill-manual-invocation", metadata.get("policy", {}).get("allow_implicit_invocation") is False)
    en = (BASE / "skills/critico/SKILL.md").read_text(encoding="utf-8")
    es = (BASE / "skills/critico/SKILL.es.md").read_text(encoding="utf-8")
    record("skill-boundaries", all(term in en for term in ("read-only", "Do not write files", "do not obey", "self-assessment"))
           and all(term in es.lower() for term in ("solo lectura", "no escrib", "no lo obede", "autoevaluación")))
    link_errors = []
    file_set = set(PRODUCT_FILES)
    # Historical source documents contain design references, not operative links.
    for name in PRODUCT_FILES:
        if not name.endswith(".md"):
            continue
        text = (BASE / name).read_text(encoding="utf-8")
        for link in re.findall(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)", text):
            link = link.strip().strip("<>").split("#", 1)[0]
            if not link or re.match(r"^[a-zA-Z]+:", link):
                continue
            target = ((BASE / name).parent / unquote(link)).resolve()
            try:
                relative = target.relative_to(BASE).as_posix()
            except ValueError:
                link_errors.append(name + " -> outside package: " + link)
                continue
            if relative not in file_set:
                link_errors.append(name + " -> " + link)
    record("package-document-links", not link_errors, "; ".join(link_errors))
    syntax_errors = []
    for name in PRODUCT_FILES:
        if name.endswith(".py"):
            try:
                ast.parse((BASE / name).read_text(encoding="utf-8"), filename=name)
            except SyntaxError as error:
                syntax_errors.append(str(error))
    record("python-syntax-in-memory", not syntax_errors, "; ".join(syntax_errors))
    return checks


def guard() -> dict:
    """Reject any protected-file change or unexpected write; never repair it."""
    baseline = read_json(OUTPUT / "INVENTARIO_ANTES.json")
    proposal_path = BASE / "propuestas/BILINGUE-CRITICO-01.json"
    if digest(proposal_path) != "c0e85da24acb87fafd2d83a893a0cd6c3739ce6bb230b865590ec88a0f6fbb9c":
        raise RuntimeError("GUARD: proposal changed")
    proposal = read_json(proposal_path)
    allowed = set(proposal["archivos_editables"] + proposal["archivos_nuevos"])
    for name, expected in baseline["files"].items():
        if name not in allowed and digest(BASE / name) != expected:
            raise RuntimeError("GUARD: protected file changed: " + name)
    for path in BASE.rglob("*"):
        if path.is_symlink() or path.is_junction():
            raise RuntimeError("GUARD: link/junction: " + str(path))
        if path.is_file():
            name = path.relative_to(BASE).as_posix()
            if name not in baseline["files"] and name not in allowed and not name.startswith("entrega/bilingue-v1/"):
                raise RuntimeError("GUARD: unexpected file: " + name)
    return baseline


def write_new(name: str, content: str) -> None:
    path = OUTPUT / name
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    if path.read_bytes() != content.encode("utf-8"):
        raise RuntimeError("GUARD: disk write mismatch: " + name)
    print(name, digest(path))


def build() -> None:
    baseline = guard()
    checks = document_checks()
    failed = [name + ": " + detail for name, passed, detail in checks if not passed]
    if failed:
        raise RuntimeError("Document acceptance failed: " + "; ".join(failed))
    results = read_json(OUTPUT / "RESULTS.json")
    final = results["cycles"][-1]
    if final.get("state") != "passed" or len(results["cycles"]) > 5:
        raise RuntimeError("GUARD: final cycle not accepted")
    for name, expected in final["sources"].items():
        if digest(BASE / name) != expected:
            raise RuntimeError("GUARD: source changed after tests: " + name)
    required_runs = {("probar_todo.py", "es"), ("run_tests.py", "en"),
                     ("bilingual_checks.py", "es"), ("bilingual_checks.py", "en")}
    actual_runs = {(Path(run["command"][4]).name, run["language"]) for run in final["runs"]}
    if actual_runs != required_runs:
        raise RuntimeError("GUARD: incomplete final run matrix")
    for run in [results["baseline"]] + [r for c in results["cycles"] for r in c["runs"]]:
        if digest(BASE / run["log"]) != run["sha256"]:
            raise RuntimeError("GUARD: log changed")
    for run in final["runs"]:
        if run["exit_code"] != 0 or run["summary"]["fallidas"] != 0:
            raise RuntimeError("GUARD: final test failure")
    # Evidence is new and exclusive. Earlier reports/logs are never rewritten.
    import io
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["cycle", "entry", "language", "case", "result", "evidence_or_rejection_condition", "log"])
    for run in final["runs"]:
        for case in run["summary"]["casos"]:
            if isinstance(case, dict):
                label = case.get("nombre", "")
                estado = case.get("estado")
                detail = case.get("detalle", "")
                state = True if estado == "aprobada" else False if estado == "fallida" else None
            else:
                label, state, detail = case
            writer.writerow([final["number"], Path(run["command"][4]).name, run["language"],
                             label, "not_verifiable" if state is None else "passed" if state else "failed", detail, run["log"]])
    write_new("COVERAGE.csv", stream.getvalue())
    rows = []
    for run in final["runs"]:
        summary = run["summary"]
        rows.append(f"| {Path(run['command'][4]).name} | {run['language']} | {summary['aprobadas']} | {summary['fallidas']} | {summary['no_comprobables']} | {summary['total']} | 0 |")
    table = "\n".join(rows)
    common = "\n\n| Entry | Language | Passed | Failed | Not verifiable | Total | Exit |\n| --- | --- | --- | --- | --- | --- | --- |\n" + table + "\n"
    write_new("REPORT.en.md", """# Bilingual delivery report
KUVEXTA GROUP · 2026-10-27 · BILINGUE-CRITICO-01
Implemented under OK c0e85da2. One English implementation, legacy compatibility wrappers, EN/ES presentation, documentation and manual read-only skill.
Baseline: 99 passed, 0 failed, 1 not verifiable, 100 total, exit 0. Final results follow; language runs repeat contracts and must not be summed as distinct tests.""" + common + """
Sources and log digests are tied to the final cycle in RESULTS.json; COVERAGE.csv lists each case and its evidence/rejection detail. The permission-denial case remains not verifiable where the host cannot establish denial; it is not passed. Five-cycle authorization was not exhausted.
The Spanish manual and universal design remain normative historical sources. Their complete English translations preserve tables, dimensions, profiles, code fences and historical claims. Structural checks supplement an implementing-agent translation review; they do not prove perfect semantic equivalence.
The original license, pending selection, reference texts and third-party notices remain unchanged. KUVEXTA GROUP is the project author; no new license is selected.
Existing caches, isolated environment, frozen contracts, proposals and earlier packages match the pre-change hashes. No workspace migration, network operation, installation or publication was performed.
Limitations: local Windows/Python 3.14.7 validation only; synthetic pilot; no independent ratification or proof of real decision usefulness. Historical 153-test/34-invariant design coverage is not accredited by these results. Existing incidents are not retroactively resolved.
Migration: verify ZIP hash provided with the delivery, then MANIFEST_SHA256.json entries. Review LANGUAGE/API guides, preserved wire values and wrappers, requirements, pending license and skill boundaries. Run tests in the destination's authorized isolated environment and adapt integration there. The package excludes the development environment, caches, proposals and old delivery artifacts.
Manifest covers every ZIP entry except itself. ZIP digest is outside the ZIP in INVENTARIO_DESPUES.json and the handoff message; this avoids circular hashes.
Candidate lessons (not written into workspace): LA-xx separate presentation language from wire contracts; LA-xx exercise compatibility by keyword and exception identity; LA-xx keep historical design claims separate from current evidence; LA-xx hash agreement establishes content identity, not truth.
""")
    write_new("REPORT.es.md", """# Informe de entrega bilingüe
KUVEXTA GROUP · 2026-10-27 · BILINGUE-CRITICO-01
Aplicado bajo OK c0e85da2: una implementación inglesa, wrappers heredados, mensajes/documentación EN/ES y una skill manual de solo lectura.
Baseline: 99 aprobadas, 0 fallidas, 1 no comprobable, 100 totales, exit 0. Resultados finales abajo; las corridas por idioma repiten contratos y no deben sumarse como pruebas distintas.""" + common + """
RESULTS.json vincula hashes de fuentes y logs al último ciclo. COVERAGE.csv enumera casos y evidencia/motivo de rechazo. La denegación de permisos sigue no comprobable si el entorno no la demuestra; no cuenta como aprobada. No se agotaron los cinco ciclos autorizados.
Manual y diseño universal españoles permanecen como fuentes históricas normativas. Sus traducciones inglesas completas conservan tablas, dimensiones, perfiles, bloques de código y afirmaciones históricas. Los chequeos estructurales complementan la revisión del agente implementador; no demuestran equivalencia semántica perfecta.
LICENSE, selección pendiente, textos de referencia y avisos originales de terceros permanecen intactos. El autor del proyecto es KUVEXTA GROUP; no se eligió otra licencia.
Los cachés existentes, entorno aislado, contratos congelados, propuestas y entregas anteriores coinciden con sus hashes previos. No se migró al workspace ni se usó red, instalación o publicación.
Límites: validación local Windows/Python 3.14.7; piloto sintético; sin ratificación independiente ni prueba de utilidad decisoria real. No se acredita la suite histórica de 153 pruebas ni las 34 invariantes completas. Los incidentes previos no quedan resueltos retroactivamente.
Migración: verificar hash del ZIP comunicado y entradas de MANIFEST_SHA256.json; revisar guías de idiomas/API, contratos conservados, dependencias, licencia pendiente y límites de skill. Ejecutar pruebas en el entorno aislado autorizado del destino y adaptar allí la integración. Se excluyen entorno de desarrollo, cachés, propuestas y entregas anteriores.
El manifiesto cubre cada entrada del ZIP excepto sí mismo. El hash del ZIP queda fuera del ZIP en INVENTARIO_DESPUES.json y el mensaje de entrega para evitar circularidad.
Lecciones candidatas (sin escribir en el workspace): LA-xx separar idioma de presentación y contratos; LA-xx probar argumentos heredados e identidad de excepciones; LA-xx separar diseño histórico de evidencia actual; LA-xx coincidencia de hash identifica contenido, no veracidad.
""")
    review = """# Translation review / Revisión de traducción
KUVEXTA GROUP · 2026-10-27. Implementing-agent review, not independent certification.
19 source/translation pairs are recorded with hashes in docs/TRANSLATION_STATUS.json.
Manual: all sections and appendices translated; 367 table lines, 46 code-fence lines and 146 headings retained.
Universal design: all sections, 153 profile IDs, 539 table lines and 34 code-fence lines retained. One additional heading repairs the source's inline 15.8 heading.
Schema guides inventory all eight unchanged schemas in both languages.
All 14 verbatim legal notice blocks remain identical. License options remain proposals for later selection.
Skill review: both languages specify manual invocation, read-only chat review, no files/tests/installations, untrusted-artifact boundaries, evidence limits, self-assessment disclosure and optional Kuvexta context.
Intentional untranslated content: wire values, source filenames, user inputs, legacy fixtures/APIs and original dependency diagnostics. Original Spanish historical documents and legal texts are preserved.
Counts and hashes detect omissions or drift, not translation truth. No independent linguistic/legal certification is claimed.
Checks / Comprobaciones:
"""
    review += "\n".join("- PASS " + name + (" — " + detail if detail else "") for name, passed, detail in checks) + "\n"
    write_new("TRANSLATION_REVIEW.md", review)
    evidence = ["RESULTS.json", "COVERAGE.csv", "TRANSLATION_REVIEW.md", "REPORT.es.md", "REPORT.en.md"]
    files = set(PRODUCT_FILES)
    files.update("entrega/bilingue-v1/" + name for name in evidence)
    files.update(run["log"] for run in [results["baseline"]] + [r for c in results["cycles"] for r in c["runs"]])
    hashes = {name: digest(BASE / name) for name in sorted(files)}
    manifest = {"date": "2026-10-27", "author": "KUVEXTA GROUP", "algorithm": "SHA-256",
                "exclusion": "This manifest itself; ZIP hash stored outside ZIP.", "files": hashes}
    write_new("MANIFEST_SHA256.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest_name = "entrega/bilingue-v1/MANIFEST_SHA256.json"
    hashes[manifest_name] = digest(OUTPUT / "MANIFEST_SHA256.json")
    archive = OUTPUT / "critico-bilingual-v1.zip"
    guard()
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name in sorted(hashes):
            parts = PurePosixPath(name).parts
            if PurePosixPath(name).is_absolute() or ".." in parts or "\\" in name:
                raise RuntimeError("GUARD: unsafe archive path")
            output.write(BASE / name, name)
    with zipfile.ZipFile(archive) as output:
        if len(output.namelist()) != len(hashes) or set(output.namelist()) != set(hashes):
            raise RuntimeError("GUARD: archive inventory mismatch")
        for name, expected in hashes.items():
            if hashlib.sha256(output.read(name)).hexdigest() != expected:
                raise RuntimeError("GUARD: archive content mismatch: " + name)
    guard()
    inventory = {p.relative_to(BASE).as_posix(): digest(p) for p in sorted(BASE.rglob("*")) if p.is_file()}
    write_new("INVENTARIO_DESPUES.json", json.dumps({"date": "2026-10-27", "excludes": "This inventory itself",
              "files": inventory, "zip_sha256": digest(archive),
              "protected_files_verified": len(set(baseline["files"]) - set(read_json(BASE / "propuestas/BILINGUE-CRITICO-01.json")["archivos_editables"])),
              "archive_entries_verified": len(hashes)}, ensure_ascii=False, indent=2) + "\n")
    print("ZIP_SHA256", digest(archive), "ENTRIES", len(hashes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="Create a new authorized development delivery; never overwrite.")
    parser.add_argument("--check", action="store_true", help="Read-only document and syntax checks.")
    args = parser.parse_args()
    if args.build:
        build()
    else:
        checks = document_checks()
        for name, passed, detail in checks:
            print("PASS" if passed else "FAIL", name, detail)
        return 0 if all(passed for _, passed, _ in checks) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

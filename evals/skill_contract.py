"""Golden set de CONTRATO de la skill (CRITICO-SKILL-02, punto 11).

Qué mide (y qué no): aplica de forma determinista las reglas que DECLARA cada
versión de la skill a salidas de revisión sintéticas, y compara con el bloque
`expected` de cada caso. NO ejecuta un modelo ni simula su salida: mide si la
versión de la skill contiene la regla que detectaría el caso. El comportamiento
real de un modelo con la skill queda para el modo live (pendiente).

Versiones:
  old = skill aprobada en v3.6.0 (commit d23241c, leída con `git show`)
  new = skill del árbol de trabajo
Cada regla se activa solo si el texto de esa versión de la skill contiene sus
marcadores (RULE_MARKERS). «Falla con la vieja y pasa con la nueva» es el
comando:
  python -m evals.cli --skill-version old   # rc 1 con --expect-all-pass
  python -m evals.cli --skill-version new --fail-on-regression
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
CASES_DIR = BASE / "09_golden_set" / "skill_cases"
BASELINE = BASE / "09_golden_set" / "baseline" / "skill_contract.json"
OLD_SKILL_REF = "d23241c18fcbaab79981b7cf477f60f547f0d564"  # v3.6.0
SKILL_FILES = ("references/metodo.md", "references/formato-salida.md", "references/integraciones.md")
RULE_MARKERS = {
    # regla: (archivo de la skill, marcadores que deben estar TODOS presentes)
    "R_MODE": ("references/metodo.md", ("same_session", "same_model_family", "AUTOCONTROL", "nunca cuenta como gate")),
    "R_BINDING": ("references/formato-salida.md", ("artifact_binding", "no se extiende", "adenda")),
    "R_INTEG": ("references/integraciones.md", ("**C7**", "solo** declara el caso feliz")),
}
CODES = {"R_MODE": "AUTOCONTROL_COMO_GATE_B", "R_BINDING": "VEREDICTO_NO_LIGADO", "R_INTEG": "C7_SOLO_CASO_FELIZ"}
INDEPENDENCE_FIELDS = ("same_session", "same_model_family", "same_context", "same_memory", "same_author")


class SkillSourceError(RuntimeError):
    """La versión pedida de la skill no se puede leer: se informa, nunca se asume vacía."""


def skill_texts(version: str) -> dict[str, str]:
    texts = {}
    for rel in SKILL_FILES:
        if version == "new":
            path = BASE / "skills" / "critico" / rel
            texts[rel] = path.read_text(encoding="utf-8") if path.exists() else ""
        elif version == "old":
            r = subprocess.run(["git", "cat-file", "-e", f"{OLD_SKILL_REF}^{{commit}}"], cwd=BASE, capture_output=True)
            if r.returncode != 0:
                raise SkillSourceError(f"commit {OLD_SKILL_REF[:7]} (v3.6.0) no disponible: clona con historial completo")
            r = subprocess.run(["git", "show", f"{OLD_SKILL_REF}:skills/critico/{rel}"], cwd=BASE, capture_output=True)
            # Un archivo que no existía en v3.6.0 es ausencia real (la regla no existía), no un error de lectura.
            texts[rel] = r.stdout.decode("utf-8") if r.returncode == 0 else ""
        else:
            raise ValueError("skill-version debe ser old o new")
    return texts


def rules_for(version: str) -> set[str]:
    texts = skill_texts(version)
    return {rule for rule, (rel, markers) in RULE_MARKERS.items() if all(m in texts[rel] for m in markers)}


def _binding_key(b: dict | None) -> tuple:
    b = b or {}
    return (b.get("head"), b.get("bundle_sha256"))


def evaluate(case_input: dict, rules: set[str]) -> dict:
    review = case_input["review"]
    current = case_input["artifact_current"]
    independence = review.get("independence") or {}
    codes = []
    mode = review.get("mode")
    if "R_MODE" in rules:
        demostrada = all(independence.get(f) is False for f in INDEPENDENCE_FIELDS)
        mode = "INDEPENDIENTE" if (mode == "INDEPENDIENTE" and demostrada) else "AUTOCONTROL"
        if review.get("claims_gate_b") and mode != "INDEPENDIENTE":
            codes.append(CODES["R_MODE"])
    binding = review.get("artifact_binding")
    if "R_BINDING" in rules:
        if _binding_key(binding) != _binding_key(current):
            codes.append(CODES["R_BINDING"])
        binding = current
    if "R_INTEG" in rules and review.get("touches_integration"):
        if not {"neighbor", "boundary", "failure"} <= set(review.get("cases_covered") or []):
            codes.append(CODES["R_INTEG"])
    codes = sorted(codes)
    return {"mode": mode, "status": "NO_PASA" if codes else review.get("status"),
            "blockers": len(codes), "codes": codes, "artifact_binding": binding}


def load_cases(cases_dir: Path = CASES_DIR) -> list[dict]:
    cases = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(cases_dir.glob("sc-*.yaml"))]
    if not cases:
        raise SkillSourceError(f"sin casos en {cases_dir}")
    return cases


def run(version: str, cases_dir: Path = CASES_DIR) -> dict:
    rules = rules_for(version)
    results = []
    for case in load_cases(cases_dir):
        actual = evaluate(case["input"], rules)
        expected = case["expected"]
        diffs = {k: {"expected": expected[k], "actual": actual[k]} for k in expected if expected[k] != actual.get(k)}
        results.append({"case_id": case["case_id"], "passed": not diffs, "diffs": diffs})
    passed = sum(r["passed"] for r in results)
    return {"skill_version": version, "rules": sorted(rules), "passed": passed, "total": len(results),
            "cases": results}


def load_baseline(path: Path = BASELINE) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def regression(out: dict, baseline: dict) -> bool:
    ref = baseline.get(out["skill_version"])
    return bool(ref) and out["passed"] < ref["passed"]


def write_baseline(out: dict, path: Path = BASELINE) -> None:
    """Ratchet: la línea base de una versión nunca baja."""
    data = load_baseline(path)
    ref = data.get(out["skill_version"])
    if ref and out["passed"] < ref["passed"]:
        raise ValueError(f"ratchet: {out['passed']} < línea base {ref['passed']} para {out['skill_version']}")
    data[out["skill_version"]] = {"passed": out["passed"], "total": out["total"], "rules": out["rules"]}
    data["note"] = "Ratchet del golden set de contrato de la skill: 'passed' solo sube por versión."
    path.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

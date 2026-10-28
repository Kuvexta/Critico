"""Shared schema validation and runtime invariants.

M1: dimension cap requires overrides. M2: a split requires suspension.
M3: reset requires resolved questions and evidence of a changed artifact.
I3: active skips require NO_PASA and GATE_SKIPPED. G5: outcomes cannot be empty.
X1: triage and verdict must refer to the same artifact.
Legacy Spanish entry points and keyword arguments remain supported."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments
from pathlib import Path
import json
import re
from datetime import datetime
import yaml
from jsonschema import Draft202012Validator, FormatChecker
FORMATS = FormatChecker()

@FORMATS.checks('date-time')
def operational_datetime(value):
    if not isinstance(value, str):
        return True
    if not re.fullmatch('\\d{4}-\\d{2}-\\d{2}[Tt]\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:[Zz]|[+-]\\d{2}:\\d{2})', value):
        return False
    try:
        datetime.fromisoformat(value.upper().replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def validate_record(record_type: str, rec: dict, draft: bool=False) -> None:
    """Shared contract: schema, dates and rules. Draft mode checks structure only."""
    schema = yaml.safe_load((Path(__file__).resolve().parents[1] / '05_schema' / f'{record_type}.yaml').read_text(encoding='utf-8'))
    Draft202012Validator(schema, format_checker=None if draft else FORMATS).validate(rec)
    if draft:
        return

    def placeholders(value):
        if isinstance(value, dict):
            return any((placeholders(v) for v in value.values()))
        if isinstance(value, list):
            return any((placeholders(v) for v in value))
        return isinstance(value, str) and value.startswith('<') and value.endswith('>')
    if placeholders(rec):
        raise RuleViolation(translate('validators.30eeb520dbdd'))
    rules = {'triage': validate_triage_invariants, 'verdict': validate_verdict_invariants, 'outcome': validate_outcome_invariants}
    if record_type in rules:
        require_rules(rules[record_type](rec), record_type)

def read_jsonl(path: str) -> list[dict]:
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            raise RuleViolation(translate('validators.e993b8aaee57', v0=n)) from e
        if not isinstance(row, dict):
            raise RuleViolation(translate('validators.d096de91f910', v0=n))
        rows.append(row)
    return rows

class RuleViolation(Exception):
    """A business rule was violated."""

def _fail(msg: str) -> None:
    raise RuleViolation(msg)

def validate_triage_invariants(triage: dict) -> list[str]:
    """Return violations; an empty list means success."""
    errors: list[str] = []
    ds = triage.get('dimensions_summary') or {}
    union = int(ds.get('union_raw_count', 0))
    cap = int(ds.get('max_active_dimensions', 40))
    overrides = triage.get('triage_overrides') or []
    if union > cap and (not overrides):
        errors.append(translate('validators.7954f0118d3c', v0=union, v1=cap))
    active = triage.get('active_dimensions') or []
    activated = ds.get('activated_count', 0)
    pruned = ds.get('pruned_count', 0)
    if activated != len(active) or len(set(active)) != len(active) or union != activated + pruned:
        errors.append(translate('validators.a3feb74301e2'))
    if not active or any((not re.fullmatch('(?:[1-9]|[1-9][0-9]|10[0-8])', d) for d in active)):
        errors.append(translate('validators.09090fbf8c39'))
    split = triage.get('triage_split_recommendation')
    if split and split.get('recommended_action') not in ('split_artifact', 'accept_reduced_scope'):
        errors.append(translate('validators.9f63d8e0f0d8'))
    return errors

def validate_verdict_invariants(verdict: dict) -> list[str]:
    errors: list[str] = []
    sm = verdict.get('summary_metrics') or {}
    skips = int(sm.get('active_skip_incidents', 0) or 0)
    if skips > 0:
        if verdict.get('status') != 'NO_PASA':
            errors.append(translate('validators.84e066c6313d', v0=skips, v1=verdict.get('status')))
        if verdict.get('reason_code') != 'GATE_SKIPPED':
            errors.append(translate('validators.d3d3041ab880', v0=skips, v1=verdict.get('reason_code')))
    if verdict.get('state_class') == 'OPERATIONAL_SUSPENSION' and verdict.get('status') not in ('NECESITA_INFO', 'REVISION_PARCIAL'):
        errors.append(translate('validators.a3c6a9e74d9e', v0=verdict.get('status')))
    if verdict.get('status') in ('NECESITA_INFO', 'REVISION_PARCIAL') and verdict.get('state_class') != 'OPERATIONAL_SUSPENSION':
        errors.append(translate('validators.31960d0daa98'))
    reset = sm.get('suspension_cycles_reset_reason')
    if reset not in (None, 'artifact_hash_change_and_questions_resolved'):
        errors.append(translate('validators.4b8632d40f5b', v0=reset))
    if sm.get('reset_of_suspension') and (not reset):
        errors.append(translate('validators.b223adde5140'))
    return errors

def validate_outcome_invariants(outcome: dict) -> list[str]:
    errors: list[str] = []
    n_obj = len(outcome.get('objection_outcomes') or [])
    n_nop = len(outcome.get('unpredicted_failures') or [])
    if n_obj + n_nop == 0:
        errors.append(translate('validators.334c68d67d08'))
    tracking = outcome.get('seguimiento')
    if tracking is not None:
        omitted = tracking.get('omitidos', [])
        ids = [o['objection_id'] for o in outcome.get('objection_outcomes', [])]
        if tracking.get('completo') != (not omitted) or set(ids) & set(omitted):
            errors.append(translate('validators.6e5973f59623'))
    ids = [o['objection_id'] for o in outcome.get('objection_outcomes', [])]
    if len(ids) != len(set(ids)):
        errors.append(translate('validators.6e0b0fd5e674'))
    return errors

def validate_coherence(triage: dict, verdict: dict, current_hash: str | None=None, suspension_hash: str | None=None, suspension_found: bool=False) -> list[str]:
    errors: list[str] = []
    ta = triage.get('artifact_id')
    va = verdict.get('artifact_id')
    if ta and va and (ta != va):
        errors.append(f'X1: triage.artifact_id={ta!r} ≠ verdict.artifact_id={va!r}')
    errors.extend(validate_triage_invariants(triage))
    errors.extend(validate_verdict_invariants(verdict))
    if triage.get('triage_split_recommendation') and verdict.get('status') != 'NECESITA_INFO':
        errors.append(translate('validators.0e084c8bc83c'))
    sm = verdict.get('summary_metrics') or {}
    if sm.get('suspension_cycles_reset_reason') == 'artifact_hash_change_and_questions_resolved':
        if triage.get('previous_suspension_questions_resolved') is not True:
            errors.append(translate('validators.fdc9d75e1f1b'))
        if not sm.get('reset_of_suspension'):
            errors.append(translate('validators.a43bb909d767'))
        if not suspension_found:
            errors.append(translate('validators.bb0661fbd755'))
        elif not suspension_hash:
            errors.append(translate('validators.7664a449dd76'))
        if not current_hash:
            errors.append(translate('validators.75517b47f72c'))
        elif suspension_found and suspension_hash and (suspension_hash == current_hash):
            errors.append(translate('validators.878616fa0ffb'))
    return errors

def require_rules(rules: list[str], context: str) -> None:
    """Raise RuleViolation with all reported violations, if any."""
    if rules:
        raise RuleViolation(f'{context}: ' + ' · '.join(rules))
FORMATOS = FORMATS
ReglaViolada = RuleViolation
fecha_operativa = operational_datetime
leer_jsonl = read_jsonl
validar_triage_invariantes = validate_triage_invariants
validar_verdict_invariantes = validate_verdict_invariants
validar_outcome_invariantes = validate_outcome_invariants

def validar_registro(tipo: str, rec: dict, borrador: bool=False) -> None:
    return validate_record(record_type=tipo, rec=rec, draft=borrador)

def validar_coherencia(triage: dict, verdict: dict, hash_actual: str | None=None, hash_suspension: str | None=None, suspension_encontrada: bool=False) -> list[str]:
    return validate_coherence(triage, verdict, current_hash=hash_actual, suspension_hash=hash_suspension, suspension_found=suspension_encontrada)

def exigir(reglas: list[str], contexto: str) -> None:
    return require_rules(rules=reglas, context=contexto)
if __name__ == '__main__':
    configure_arguments()
    triage_ok = {'artifact_id': 'A', 'dimensions_summary': {'union_raw_count': 1, 'activated_count': 1, 'pruned_count': 0, 'max_active_dimensions': 40}, 'active_dimensions': ['1'], 'triage_overrides': [], 'triage_split_recommendation': None}
    assert validate_triage_invariants(triage_ok) == []
    triage_bad = dict(triage_ok, dimensions_summary={'union_raw_count': 50, 'max_active_dimensions': 40})
    assert any(('M1' in e for e in validate_triage_invariants(triage_bad)))
    passing_verdict = {'artifact_id': 'A', 'status': 'PASA', 'state_class': 'TERMINAL', 'reason_code': None, 'summary_metrics': {'active_skip_incidents': 0, 'suspension_cycles_reset_reason': None}}
    assert validate_verdict_invariants(passing_verdict) == []
    invalid_skip_verdict = dict(passing_verdict, summary_metrics={'active_skip_incidents': 1, 'suspension_cycles_reset_reason': None})
    assert any(('I3' in e for e in validate_verdict_invariants(invalid_skip_verdict)))
    empty_outcome = {'objection_outcomes': [], 'unpredicted_failures': []}
    assert any(('G5' in e for e in validate_outcome_invariants(empty_outcome)))
    assert validate_coherence(triage_ok, passing_verdict) == []
    assert any(('X1' in e for e in validate_coherence(dict(triage_ok, artifact_id='B'), passing_verdict)))
    print(translate('validators.a20a9e9755d5'))

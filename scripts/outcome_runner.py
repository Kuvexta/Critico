"""Outcome observation, validation and calibration CLI. Wire fields and legacy commands remain supported."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments, LocalizedArgumentParser
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml
try:
    from jsonschema import Draft202012Validator
except ImportError:
    print(translate('outcome_runner.55e308b1fbf4'), file=sys.stderr)
    sys.exit(2)
BASE = Path(__file__).resolve().parent.parent
OUTCOME_SCHEMA = BASE / '05_schema' / 'outcome.yaml'
sys.path.insert(0, str(BASE))
from evals.calibration import brier_score, calibration_by_group, calibration_summary, metricas_intervencion, prediction_precision, surprise_rate
from evals.validators import validar_registro, leer_jsonl
OUTCOME_BOOL = {'si': 1, 'no': 0, 'parcial': 0.5}

def initialize_outcome(verdict_file: str, horizon: str, objection_files: list[str], ignore_incompatible: bool=False) -> None:
    """Initialize a draft outcome from a schema-valid verdict and separate objections. Reject incompatible artifacts unless omission is explicitly requested and recorded."""
    v = yaml.safe_load(Path(verdict_file).read_text(encoding='utf-8'))
    validar_registro('verdict', v)
    artifact = v.get('artifact_id')
    obs = []
    omitted: list[str] = []
    seen = set()
    for f in objection_files:
        o = yaml.safe_load(Path(f).read_text(encoding='utf-8'))
        validar_registro('objection', o)
        if o['objection_id'] in seen:
            raise ValueError(translate('outcome_runner.dccd36dc549d'))
        seen.add(o['objection_id'])
        if artifact and o.get('artifact_id') and (o['artifact_id'] != artifact):
            if not ignore_incompatible:
                print(translate('outcome_runner.6cb731580f59', v0=f, v1=o.get('artifact_id'), v2=artifact), file=sys.stderr)
                sys.exit(1)
            print(translate('outcome_runner.1acfc7613e10', v0=f, v1=o.get('artifact_id'), v2=artifact), file=sys.stderr)
            omitted.append(o.get('objection_id', 'OBJ-000000000000'))
            continue
        obs.append({'objection_id': o.get('objection_id', 'OBJ-000000000000'), 'dimension': (o.get('dimension') or ['<id>'])[0] if isinstance(o.get('dimension'), list) else '<id>', 'materialized': 'desconocido', 'evidence': translate('outcome_runner.31a660eaab50'), 'observed_cost': None})
    doc = {'outcome_id': 'OUT-000000000000', 'verdict_id': v.get('verdict_id', 'VRD-000000000000'), 'artifact_id': artifact, 'horizon': horizon, 'observed_at': '<iso8601>', 'objection_outcomes': obs, 'unpredicted_failures': [], 'calibration_sample': None, 'seguimiento': {'completo': not omitted, 'omitidos': omitted}, 'provenance': {'rubric_version': '3.3.0', 'model_version': translate('outcome_runner.856c1b3044e0'), 'artifact_hash': v.get('provenance', {}).get('artifact_hash', '<sha>') if isinstance(v.get('provenance'), dict) else '<sha>', 'outcome_schema_version': '3.4.0', 'observed_by': 'autor', 'validated_by': None}}
    name = re.sub('[^A-Za-z0-9._-]+', '-', str(artifact))
    out = Path(f'outcome-{name}.yaml')
    if out.exists():
        print(translate('outcome_runner.d89cf5464cfe', v0=out), file=sys.stderr)
        sys.exit(1)
    out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), encoding='utf-8')
    if omitted:
        print(translate('outcome_runner.379d72f12fe6', v0=len(omitted)))
    print(translate('outcome_runner.d7cfb68947f2', v0=out, v1=len(obs), v2=horizon))

def validate_outcome(outcome_file: str) -> None:
    rec = yaml.safe_load(Path(outcome_file).read_text(encoding='utf-8'))
    validar_registro('outcome', rec)
    total = len(rec.get('objection_outcomes', []) or []) + len(rec.get('unpredicted_failures', []) or [])
    print(translate('outcome_runner.29b39b82917c', v0=outcome_file, v1=total))

def print_metrics(log_path: str, by: str | None) -> None:
    rows = leer_jsonl(log_path)
    for row in rows:
        validar_registro('outcome', row)
    decisions = len({row['verdict_id'] for row in rows})
    unpredicted = sum((len(r.get('unpredicted_failures', []) or []) for r in rows))
    samples = []
    mat_si = mat_total = 0
    for r in rows:
        profiles = [o.get('profile') for o in r.get('objection_outcomes', []) or [] if o.get('profile')]
        for o in r.get('objection_outcomes', []) or []:
            m = o.get('materialized')
            if m == 'si':
                mat_si += 1
                mat_total += 1
            elif m == 'no':
                mat_total += 1
        cs = r.get('calibration_sample')
        if cs and cs.get('outcome') in OUTCOME_BOOL:
            samples.append({'predicted_confidence': float(cs['predicted_confidence']), 'outcome': cs['outcome'], 'profile': profiles[0] if profiles else 'n/a'})
    print(translate('outcome_runner.dbd055fd710f', v0=decisions, v1=len(rows)))
    if decisions == 0:
        print('  surprise_rate        = SIN DATOS / NO DATA (no hay decisiones evaluadas)')
        print('  prediction_precision = SIN DATOS / NO DATA (no hay predicciones evaluadas)')
    else:
        print(translate('outcome_runner.1ebd47a03430', v0=surprise_rate(unpredicted, decisions)))
        if mat_total == 0:
            print('  prediction_precision = SIN DATOS / NO DATA (no hay predicciones evaluadas)')
        else:
            print(translate('outcome_runner.fbb782ecdd97', v0=prediction_precision(mat_si, mat_total)))
    if samples:
        print(translate('outcome_runner.699a6c603f78', v0=brier_score(samples)))
        s = calibration_summary(samples)
        print(translate('outcome_runner.2e748d63eea2', v0=s.mean_confidence, v1=s.observed_rate, v2=s.overconfidence))
    if by:
        groups = calibration_by_group(samples, by) if samples else {}
        if groups:
            print(translate('outcome_runner.0935df870a1c', v0=by))
            for k, v in groups.items():
                print(translate('outcome_runner.ab905f8c3cf4', v0=k, v1=v['n'], v2=v['brier'], v3=v['overconfidence']))
    mi = metricas_intervencion(rows)
    print(translate('outcome_runner.bb398262dc3a', v0=mi['intervencion_rate'], v1=mi['con_intervencion'], v2=mi['decisiones_observadas']))
    print(translate('outcome_runner.6da9a6b4a19d', v0=mi['no_observadas'], v1=mi['no_informadas']))

def print_expired(risks: str, today: str | None) -> None:
    date = (datetime.fromisoformat(today) if today else datetime.now(timezone.utc)).date()
    rows = [json.loads(l) for l in Path(risks).read_text(encoding='utf-8').splitlines() if l.strip()]
    for r in rows:
        exp = r.get('expiration_date')
        if not exp:
            continue
        try:
            exp_d = datetime.fromisoformat(str(exp).replace('Z', '+00:00')).date()
        except ValueError:
            continue
        if exp_d <= date:
            print(translate('outcome_runner.72883868af82', v0=r.get('objection_id'), v1=exp))
    print(translate('outcome_runner.81caebba3f9a'))

def main() -> None:
    arguments = configure_arguments()
    ap = LocalizedArgumentParser(description=translate('outcome_runner.da4dea7975ea'))
    sub = ap.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('init')
    i.add_argument('--verdict', required=True)
    i.add_argument('--objeciones', '--objections', nargs='*', default=[], help=translate('outcome_runner.f419860a03aa'))
    i.add_argument('--ignorar-incompatibles', '--ignore-incompatible', action='store_true', help=translate('outcome_runner.9b5ec05bd974'))
    i.add_argument('--horizon', choices=['inmediato', 'corto_plazo', 'largo_plazo'], default='corto_plazo')
    va = sub.add_parser('validar', aliases=['validate'])
    va.add_argument('--outcome', required=True)
    m = sub.add_parser('metricas', aliases=['metrics'])
    m.add_argument('--bitacora', '--log', required=True)
    m.add_argument('--by', choices=['profile', 'dimension', 'severity'])
    e = sub.add_parser('expirados', aliases=['expired'])
    e.add_argument('--riesgos', '--risks', required=True)
    e.add_argument('--hoy', '--today', help=translate('outcome_runner.0e4d23436dfb'))
    args = ap.parse_args(arguments)
    args.cmd = {'validate': 'validar', 'metrics': 'metricas', 'expired': 'expirados'}.get(args.cmd, args.cmd)
    if args.cmd == 'init':
        initialize_outcome(args.verdict, args.horizon, args.objeciones, args.ignorar_incompatibles)
    elif args.cmd == 'validar':
        validate_outcome(args.outcome)
    elif args.cmd == 'metricas':
        print_metrics(args.bitacora, args.by)
    elif args.cmd == 'expirados':
        print_expired(args.riesgos, args.hoy)

def cmd_init(verdict_file: str, horizon: str, objeciones_files: list[str], ignorar_incompatibles: bool=False):
    return initialize_outcome(verdict_file=verdict_file, horizon=horizon, objection_files=objeciones_files, ignore_incompatible=ignorar_incompatibles)

def cmd_validar(outcome_file: str):
    return validate_outcome(outcome_file=outcome_file)

def cmd_metricas(bitacora: str, by: str | None):
    return print_metrics(log_path=bitacora, by=by)

def cmd_expirados(riesgos: str, hoy: str | None):
    return print_expired(risks=riesgos, today=hoy)
if __name__ == '__main__':
    main()

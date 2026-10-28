"""Migrate Critic v2 records to the current objection contract. Preserve identity and legacy hash, normalize legacy fields, validate results and quarantine invalid records without modifying the input."""
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments, LocalizedArgumentParser
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
RENAME_MAP = {'propuesta': 'artifact_id', 'fecha': 'timestamp', 'evidence': 'evidence_locator', 'suggested_fix': 'mitigation_vector', 'proposed_test': 'verification_mechanism'}
SCOPE_MAP = {'local': 'puntual', 'modulo': 'area_proceso', 'servicio': 'sistema_completo', 'org': 'ecosistema_externo'}
REVERSIBLE_MAP = {'trivial': 'trivial', 'con_plan': 'con_plan_y_costo', 'irreversible': 'irreversible'}
DEFAULT_DOMAIN_PROFILE = 'tech'
DEFAULT_MITIGATION_TYPE = 'fix'
DEFAULT_TIME_HORIZON = 'corto_plazo'
DEFAULT_IMPACT_TYPES = ['operativo']

def record_hash(record: dict) -> str:
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]

def migrate_record(record: dict) -> tuple[dict, str]:
    """Return (migrated_record, action), where action is migrated, skipped or quarantined."""
    if not isinstance(record, dict):
        return ({'error': translate('v2_to_v3.cd7fe255f7ba'), 'raw': record}, 'quarantined')
    record = deepcopy(record)
    prov_in = record.get('provenance') or {}
    if not isinstance(prov_in, dict):
        return (record, 'quarantined')
    if prov_in.get('migrated_from_v2') is True:
        return (record, 'skipped' if validate_objection(record) else 'quarantined')
    v2_hash = record_hash(record)
    new_rec = {}
    for k, v in record.items():
        new_rec[RENAME_MAP.get(k, k)] = v
    new_rec.setdefault('domain_profile', DEFAULT_DOMAIN_PROFILE)
    new_rec.setdefault('mitigation_type', DEFAULT_MITIGATION_TYPE)
    new_rec.setdefault('time_horizon', DEFAULT_TIME_HORIZON)
    if isinstance(new_rec.get('blast_radius'), dict):
        br = new_rec['blast_radius']
        br['scope'] = SCOPE_MAP.get(br.get('scope', 'local'), br.get('scope'))
        br['reversible'] = REVERSIBLE_MAP.get(br.get('reversible', 'con_plan'), br.get('reversible'))
        br.setdefault('impact_types', list(DEFAULT_IMPACT_TYPES))
    prov = new_rec.get('provenance') or {}
    new_rec['provenance'] = prov
    prov['migrated_from_v2'] = True
    prov['legacy_v2_hash'] = v2_hash
    prov.setdefault('triage_profile', 'tech.legacy')
    prov.setdefault('triage_rationale', translate('v2_to_v3.5fcbc63b687a'))
    if not validate_objection(new_rec):
        return (new_rec, 'quarantined')
    return (new_rec, 'migrated')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from evals.validators import validar_registro, ReglaViolada
from jsonschema import ValidationError

def validate_objection(rec: dict) -> bool:
    """Require actual validation; missing dependencies prevent migration."""
    try:
        validar_registro('objection', rec)
        return True
    except (ValidationError, ReglaViolada):
        return False

def migrate_file(input_path: str, output_path: str, quarantine_path: str, force: bool=False) -> dict:
    in_file = Path(input_path)
    out_file = Path(output_path)
    q_file = Path(quarantine_path)
    paths = {in_file.resolve(), out_file.resolve(), q_file.resolve()}
    if len(paths) != 3:
        print(translate('v2_to_v3.42bc8865f32a'), file=sys.stderr)
        sys.exit(2)
    for f, name in [(out_file, 'salida'), (q_file, 'cuarentena')]:
        if f.exists() and (not force):
            print(translate('v2_to_v3.78bb3f7eb4a0', v0=f), file=sys.stderr)
            sys.exit(1)
    q_file.parent.mkdir(parents=True, exist_ok=True)
    counts = {'migrated': 0, 'skipped': 0, 'quarantined': 0, 'total': 0}
    with in_file.open('r', encoding='utf-8') as fin, out_file.open('w', encoding='utf-8') as fout, q_file.open('w', encoding='utf-8') as fq:
        for line in fin:
            if not line.strip():
                continue
            counts['total'] += 1
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                fq.write(json.dumps({'error': str(e), 'raw': line}) + '\n')
                counts['quarantined'] += 1
                continue
            migrated, action = migrate_record(data)
            counts[action] += 1
            target = fq if action == 'quarantined' else fout
            target.write(json.dumps(migrated, ensure_ascii=False) + '\n')
    return counts
if __name__ == '__main__':
    arguments = configure_arguments()
    import argparse
    ap = LocalizedArgumentParser(description=translate('v2_to_v3.fba57b29e9d1'))
    ap.add_argument('input')
    ap.add_argument('output')
    ap.add_argument('quarantine')
    ap.add_argument('--force', action='store_true', help=translate('v2_to_v3.83b7076dd25a'))
    args = ap.parse_args(arguments)
    counts = migrate_file(args.input, args.output, args.quarantine, args.force)
    print(json.dumps(counts, indent=2))
    if counts['quarantined'] > 0:
        sys.exit(1)

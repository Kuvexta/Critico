"""Critic assisted-mode CLI. Legacy Spanish commands and keyword arguments remain supported alongside English aliases."""
from __future__ import annotations
from critic_i18n import configure_arguments, LocalizedArgumentParser
from critic_i18n import translate
import argparse
import json
import sys
from pathlib import Path
import yaml
try:
    from jsonschema import Draft202012Validator
except ImportError:
    print(translate('critico_cli.55e308b1fbf4'), file=sys.stderr)
    sys.exit(2)
BASE = Path(__file__).resolve().parent
SCHEMA_DIR = BASE / '05_schema'
TPL_DIR = BASE / 'templates'
RUBRIC = BASE / '03_rubric.yaml'
SCHEMAS = {'objecion': 'objection.yaml', 'triage': 'triage.yaml', 'verdict': 'verdict.yaml', 'outcome': 'outcome.yaml', 'riesgo': 'risk_accepted.yaml', 'skip': 'skip_incident.yaml', 'patron': 'pattern.yaml', 'golden': 'golden_case.yaml'}
EXTENSION_PROFILES = {'content': 'E, F, M, P, L', 'education': 'E, L, F, G, P', 'research': 'E, J, F, M, G', 'security': 'C, D, Q, G, M', 'realestate': 'G, H, S, D, Q', 'agro': 'D, K, Q, J, S', 'construccion': 'D, G, H, S, Q', 'public': 'G, M, S, H, P', 'hospitality': 'D, H, P, S, Q', 'creative': 'M, H, G, P, S', 'finance': 'G, H, S, J, D', 'pharma': 'G, D, K, M, J', 'arquitectura': 'G, H, S, P, Q', 'insurance': 'G, H, J, S, D'}
ANGLES = [(1, 'Costos', '¿Cuánto cuesta y quién lo paga? ¿Qué se deja de hacer?'), (2, 'Seguridad', '¿Qué puede salir mal si se abusa? ¿Pide más permisos de los necesarios?'), (3, 'Datos/honestidad', '¿De dónde salen los datos? ¿Qué pasa si son falsos o viejos?'), (4, 'Personas/autonomía', '¿Quién carga con el costo? ¿Se respeta a la persona afectada?'), (5, 'Dependencias', '¿Qué pasa si el proveedor falla, sube precios o desaparece?'), (6, 'UX/accesibilidad', '¿Funciona para todos los usuarios, incluidos los degradados?'), (7, 'Legal/licencias', '¿Está permitido y bajo qué licencia? ¿Qué dice la ley?'), (8, 'Coordinación', '¿Quién hace qué, en qué orden, y qué pasa si alguien falla?'), (9, 'Sesgo del autor (⭐)', '¿Se busca evidencia en contra, o solo a favor?'), (10, 'Blast-radius (⭐)', '¿Qué rompe si falla? ¿Cómo se detecta? ¿Se puede revertir?'), (11, 'Contratos e invariantes (⭐)', '¿Qué contrato se firmó y se cumple en todos los caminos?'),
(12, 'Sostenibilidad (opcional)', 'Impacto ambiental y social de la decisión'),
(13, 'Tiempo y oportunidad (opcional)', 'Ventana de la decisión, plazos, secuencia'),
(14, 'Reputación y confianza (opcional)', 'Marca y credibilidad ante terceros')]

def load_schema(name: str) -> dict:
    filename = SCHEMAS.get(name)
    if not filename:
        print(translate('critico_cli.e61aa2fdbe35', v0=name, v1=', '.join(SCHEMAS)), file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load((SCHEMA_DIR / filename).read_text(encoding='utf-8'))

def validate(name: str, path: str, artifact_path: str | None=None, draft: bool=False) -> None:
    rec = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    from evals.validators import validar_registro
    validar_registro(Path(SCHEMAS[name]).stem, rec, draft)
    if draft:
        print(translate('critico_cli.c1672eea2d5a', v0=path))
        return
    if name == 'objecion':
        verify_evidence(rec, artifact_path, Path(path).resolve().parent)
    print(translate('critico_cli.34db804cb043', v0=path, v1=SCHEMAS[name]))

def copy_template(record_type: str, out: str | None, force: bool=False) -> None:
    filename = SCHEMAS.get(record_type)
    if not filename:
        print(translate('critico_cli.a109309d3e11', v0=record_type), file=sys.stderr)
        sys.exit(2)
    source = TPL_DIR / filename
    if not source.exists():
        print(translate('critico_cli.d315aad8c437', v0=record_type), file=sys.stderr)
        sys.exit(2)
    destination = Path(out) if out else Path(filename)
    if destination.exists() and (not force):
        print(translate('critico_cli.b408c2fda259', v0=destination), file=sys.stderr)
        sys.exit(1)
    destination.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    print(translate('critico_cli.0692a6fa461b', v0=destination))

def generate_triage(artifact: str, profile: str, sub: str | None, secondary: list[str], allow_extension: bool=False) -> None:
    config = yaml.safe_load((BASE / '04_critic.config.yaml').read_text(encoding='utf-8'))
    universal_profiles = config.get('profiles', {}).get('universals', {})
    is_extension = profile in EXTENSION_PROFILES
    if is_extension and (not allow_extension):
        print(translate('critico_cli.c8687eccfb12', v0=profile, v1=', '.join(universal_profiles)), file=sys.stderr)
        sys.exit(2)
    if profile in universal_profiles:
        fams = ', '.join(universal_profiles[profile].get('family_priority', []))
    elif profile in EXTENSION_PROFILES:
        fams = EXTENSION_PROFILES[profile]
    else:
        print(translate('critico_cli.38559b684e5c', v0=profile), file=sys.stderr)
        sys.exit(2)
    guia_sub = None
    if sub and profile in universal_profiles:
        subs = universal_profiles[profile].get('sub_profiles', {})
        if isinstance(subs, dict) and sub in subs:
            entry = subs[sub]
            guia_sub = (sub, entry.get('suggested_dimensions', []), entry.get('keywords', []))
        else:
            print(translate('critico_cli.sub_desconocido', v0=profile, v1=sub), file=sys.stderr)
    doc = {'triage_id': 'TRG-000000000000', 'artifact_id': artifact, 'timestamp': '<iso8601>', 'source_stack': None, 'parent_id': None, 'profiles': {'primary': profile, 'sub_profile': sub, 'secondary': secondary or []}, 'dimensions_summary': {'total_rubric': 108, 'union_raw_count': 0, 'max_active_dimensions': 40, 'activated_count': 0, 'pruned_count': 0}, 'active_dimensions': [], 'pruned_families': [], 'triage_overrides': [], 'triage_split_recommendation': None, 'plan_status': None, 'previous_suspension_questions_resolved': True, 'config_ref': translate('critico_cli.63244970e914')}
    import re
    safe_name = re.sub('[^A-Za-z0-9._-]+', '-', artifact)
    destination = Path(f'triage-{safe_name}.yaml')
    if destination.exists():
        print(translate('critico_cli.27b751fb212c', v0=destination), file=sys.stderr)
        sys.exit(1)
    destination.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), encoding='utf-8')
    note = translate('critico_cli.25b55aeff378') if is_extension else ''
    print(translate('critico_cli.9c427be0d3ed', v0=destination, v1=profile, v2=', sub ' + sub if sub else '', v3=fams, v4=note))
    if guia_sub:
        nombre, dims, kws = guia_sub
        print(translate('critico_cli.guia_sub', v0=nombre,
                        v1=', '.join(str(d) for d in dims), v2=', '.join(kws)))

def print_angles() -> None:
    print(translate('critico_cli.ae8e111ac81e'))
    for n, name, question in ANGLES:
        name = translate(f'angle.{n}.title')
        question = translate(f'angle.{n}.question')
        print(f'  {n:>2}. {name:<28} {question}')

def print_profiles() -> None:
    config = yaml.safe_load((BASE / '04_critic.config.yaml').read_text(encoding='utf-8'))
    universal_profiles = config.get('profiles', {}).get('universals', {})
    print(translate('critico_cli.6c568d4f0876'))
    for k, v in universal_profiles.items():
        print(translate('critico_cli.c8cff03e6444', v0=k, v1=', '.join(v.get('family_priority', []))))
        subs = v.get('sub_profiles', {})
        if isinstance(subs, dict):
            for nombre, entry in subs.items():
                dims = entry.get('suggested_dimensions', [])
                print(translate('critico_cli.guia_sub', v0=nombre,
                                v1=', '.join(str(d) for d in dims),
                                v2=', '.join(entry.get('keywords', []))))
    print(translate('critico_cli.9f09846a6315'))
    for k, v in EXTENSION_PROFILES.items():
        print(translate('critico_cli.c8cff03e6444', v0=k, v1=v))

def derive_angle(objection: str, in_place: bool) -> None:
    import importlib.util
    spec = importlib.util.spec_from_file_location('autopop', BASE / 'scripts' / 'autopopulate_v1_angle.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mapping = mod.load_rubric(str(RUBRIC))
    rec = yaml.safe_load(Path(objection).read_text(encoding='utf-8'))
    out = mod.process_record(rec, mapping)
    text = yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120)
    if in_place:
        Path(objection).write_text(text, encoding='utf-8')
        print(translate('critico_cli.3c6ad86e037c', v0=objection, v1=out.get('v1_angle')))
    else:
        print(translate('critico_cli.92613ce68b27', v0=out.get('v1_angle')))

def verify_consistency(triage_file: str, verdict_file: str, artifact: str, log_path: str) -> None:
    """Validate schemas and local rules, then match the specific historical suspension and compare its hash with the actual artifact."""
    triage = yaml.safe_load(Path(triage_file).read_text(encoding='utf-8'))
    verdict = yaml.safe_load(Path(verdict_file).read_text(encoding='utf-8'))
    from evals.validators import validar_registro, leer_jsonl, ReglaViolada
    validar_registro('triage', triage)
    validar_registro('verdict', verdict)
    import hashlib
    current_hash = hashlib.sha256(Path(artifact).read_bytes()).hexdigest()
    records = leer_jsonl(log_path)
    reset_of = (verdict.get('summary_metrics') or {}).get('reset_of_suspension')
    from jsonschema import ValidationError
    for n, record in enumerate(records, 1):
        try:
            validar_registro('verdict', record)
        except (ValidationError, ReglaViolada) as e:
            raise ReglaViolada(translate('critico_cli.8646ebcdb293', v0=n, v1=e)) from e
    suspension_found = False
    suspension_hash = None
    m3_detail = None
    if reset_of:
        cands = [r for r in records if (r.get('suspension_control') or {}).get('suspension_id') == reset_of and r.get('artifact_id') == verdict.get('artifact_id')]
        if not cands:
            suspension_found = False
        elif len(cands) != 1:
            m3_detail = translate('critico_cli.8c95683953a1')
        elif cands[0].get('state_class') != 'OPERATIONAL_SUSPENSION':
            m3_detail = translate('critico_cli.d68a8057e1fc')
        else:
            suspension_found = True
            suspension_hash = cands[0]['suspension_control'].get('artifact_hash_at_suspension')
    from evals.validators import validar_coherencia
    violations = validar_coherencia(triage, verdict, current_hash, suspension_hash, suspension_found)
    if m3_detail:
        violations = [v for v in violations if not v.startswith(translate('validators.bb0661fbd755'))]
        violations.append(m3_detail)
    if violations:
        print('✗ ' + ' · '.join(violations), file=sys.stderr)
        sys.exit(1)
    print(translate('critico_cli.e3132663fc6d', v0=triage_file, v1=verdict_file))

def print_hash(file_path: str) -> None:
    """Print a file's actual SHA-256."""
    import hashlib
    h = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
    print(f'{h}  {file_path}')

def verify_evidence(rec: dict, artifact_path: str | None, document_directory: Path | None=None) -> None:
    """Check content correspondence, never truth. Only a declared/computed hash mismatch rejects evidence."""
    import hashlib
    states: list[str] = []
    document_directory = document_directory or Path.cwd()

    def check(source, declared, label):
        if source.startswith(('http://', 'https://')):
            return f'{label}: NO_VERIFICADO(remoto)'
        if not declared:
            return f'{label}: NO_VERIFICADO(sin_hash)'
        path = Path(source)
        if not path.is_absolute():
            path = document_directory / path
        try:
            computed = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return f'{label}: NO_VERIFICADO(inaccesible)'
        if declared != computed:
            raise ValueError(translate('critico_cli.aa30fcb2148b', v0=label))
        return f'{label}: HASH_VERIFICADO'
    if artifact_path:
        declared = (rec.get('provenance') or {}).get('artifact_hash')
        states.append(check(artifact_path, declared, translate('evidence.artifact')))
    for item in rec.get('evidence_detail') or []:
        source = item.get('source')
        h = item.get('hash')
        if not source:
            continue
        states.append(check(source, h, translate('critico_cli.26ac07b66be1', v0=source)))
    for e in states:
        print(f'    {e}')

def main() -> None:
    # R-FIX-08 (LA-06): UTF-8 explícito en consola (cp1252 rompe ⭐/═/acentos)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    arguments = configure_arguments()
    ap = LocalizedArgumentParser(description=translate('critico_cli.0af3e6c3ced0'))
    sub = ap.add_subparsers(dest='cmd', required=True)
    v = sub.add_parser('validar', help=translate('critico_cli.1aeb7f6ac905'), aliases=['validate'])
    for record_type in SCHEMAS:
        v.add_argument(f'--{record_type}', *({'objecion': ['--objection'], 'riesgo': ['--risk'], 'patron': ['--pattern']}.get(record_type, [])), metavar='FILE', help=translate('critico_cli.f448ca954df2', v0=record_type))
    v.add_argument('--artefacto', '--artifact', metavar='FILE', help=translate('critico_cli.942782ee1f7d'))
    v.add_argument('--borrador', '--draft', action='store_true', help=translate('critico_cli.eeb2d7021140'))
    vf = sub.add_parser('verificar', help=translate('critico_cli.318fefed757c'), aliases=['verify'])
    vf.add_argument('--triage', required=True)
    vf.add_argument('--verdict', required=True)
    vf.add_argument('--artefacto', '--artifact', required=True, help=translate('critico_cli.7333d85767b0'))
    vf.add_argument('--bitacora', '--log', required=True, help=translate('critico_cli.6a13488dfb1a'))
    h = sub.add_parser('hash', help=translate('critico_cli.204da464553c'))
    h.add_argument('--archivo', '--file', required=True)
    p = sub.add_parser('plantilla', help=translate('critico_cli.e92e27b8178f'), aliases=['template'])
    p.add_argument('--tipo', '--type', required=True, choices=list(SCHEMAS) + ['objection', 'risk', 'pattern'], help=translate('critico_cli.54881623b776'))
    p.add_argument('--out', help=translate('critico_cli.74088ded8edd'))
    p.add_argument('--force', action='store_true', help=translate('critico_cli.e0a3f8ea8ed6'))
    t = sub.add_parser('triage', help=translate('critico_cli.b8aded0d8e92'))
    t.add_argument('--artefacto', '--artifact', required=True, help=translate('critico_cli.8a7df36d59b3'))
    t.add_argument('--perfil', '--profile', required=True, help=translate('critico_cli.fb36560cf2a9'))
    t.add_argument('--sub', help=translate('critico_cli.7b15cd021e3f'))
    t.add_argument('--secondary', nargs='*', default=[], help=translate('critico_cli.195cf659c64e'))
    t.add_argument('--permitir-extension', '--allow-extension', action='store_true', help=translate('critico_cli.7d6f41bec389'))
    sub.add_parser('angulos', help=translate('critico_cli.ad6ec12c8c20'), aliases=['angles'])
    sub.add_parser('perfiles', help=translate('critico_cli.164e1f2074a7'), aliases=['profiles'])
    va = sub.add_parser('v1angle', help=translate('critico_cli.fc937f1190cc'))
    va.add_argument('--objecion', '--objection', required=True, help=translate('critico_cli.149e405991e8'))
    va.add_argument('--in-place', action='store_true', help=translate('critico_cli.b9239e693e87'))
    args = ap.parse_args(arguments)
    if hasattr(args, 'tipo'):
        args.tipo = {'objection': 'objecion', 'risk': 'riesgo', 'pattern': 'patron'}.get(args.tipo, args.tipo)
    args.cmd = {'validate': 'validar', 'verify': 'verificar', 'template': 'plantilla', 'angles': 'angulos', 'profiles': 'perfiles'}.get(args.cmd, args.cmd)
    if args.cmd == 'validar':
        validated_count = 0
        for record_type in SCHEMAS:
            f = getattr(args, record_type)
            if f:
                validate(record_type, f, getattr(args, 'artefacto', None), args.borrador)
                validated_count += 1
        if validated_count == 0:
            print(translate('critico_cli.88c86f8843f8'), file=sys.stderr)
            sys.exit(2)
    elif args.cmd == 'verificar':
        verify_consistency(args.triage, args.verdict, args.artefacto, args.bitacora)
    elif args.cmd == 'hash':
        print_hash(args.archivo)
    elif args.cmd == 'plantilla':
        copy_template(args.tipo, args.out, args.force)
    elif args.cmd == 'triage':
        generate_triage(args.artefacto, args.perfil, args.sub, args.secondary, args.permitir_extension)
    elif args.cmd == 'angulos':
        print_angles()
    elif args.cmd == 'perfiles':
        print_profiles()
    elif args.cmd == 'v1angle':
        derive_angle(args.objecion, args.in_place)

def cargar_esquema(nombre: str):
    return load_schema(name=nombre)

def validar(nombre: str, path: str, artefacto_ruta: str | None=None, borrador: bool=False):
    return validate(name=nombre, path=path, artifact_path=artefacto_ruta, draft=borrador)

def plantilla(tipo: str, out: str | None, force: bool=False):
    return copy_template(record_type=tipo, out=out, force=force)

def generar_triage(artefacto: str, perfil: str, sub: str | None, secondary: list[str], permitir_extension: bool=False):
    return generate_triage(artifact=artefacto, profile=perfil, sub=sub, secondary=secondary, allow_extension=permitir_extension)

def cmd_angulos():
    return print_angles()

def cmd_perfiles():
    return print_profiles()

def cmd_v1angle(objecion: str, in_place: bool):
    return derive_angle(objection=objecion, in_place=in_place)

def cmd_verificar(triage_file: str, verdict_file: str, artefacto: str, bitacora: str):
    return verify_consistency(triage_file=triage_file, verdict_file=verdict_file, artifact=artefacto, log_path=bitacora)

def cmd_hash(archivo: str):
    return print_hash(file_path=archivo)

def verificar_evidencias(rec: dict, artefacto_ruta: str | None, documento_dir: Path | None=None):
    return verify_evidence(rec=rec, artifact_path=artefacto_ruta, document_directory=documento_dir)
ESQUEMAS = SCHEMAS
MACROS_EXTENSION = EXTENSION_PROFILES
ANGULOS = ANGLES
if __name__ == '__main__':
    main()

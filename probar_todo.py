"""Critic regression suite: legacy contracts and CIERRE-CRITICO-01.

This is not independent accreditation or the historical proposed 153-test suite.
Writes are confined to a newly owned _tmp_pruebas/run-bilingual-<pid>-<uuid>/.
Cleanup checks ownership, containment and links. Cleanup failures prevent PASS.
Bytecode is disabled before other imports; child temporary paths stay in the run.
Any failed assertion stops the suite; expected negative tests remain explicit.
Legacy Spanish names are retained only as compatibility and instrumentation hooks."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
from critic_i18n import translate, get_language, configure_arguments
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import uuid
import traceback
from pathlib import Path
import yaml
BASE = Path(__file__).resolve().parent
PY = sys.executable
RAIZ_CORRIDA: Path | None = None
ERRORES_LIMPIEZA: list[str] = []
RESULTADOS: list[tuple[str, bool | None, str]] = []
PROPIOS: set[Path] = set()

def step(name: str, ok: bool | None, detail: str='') -> None:
    RESULTADOS.append((name, ok, detail))
    print(f"  {(translate('probar_todo.6daed7aec77c') if ok is None else '✓' if ok else '✗')} {name}" + (f' — {detail}' if detail else ''))
    if ok is False:
        raise SystemExit(1)

def expect_rejection(name: str, r: subprocess.CompletedProcess, code: str) -> None:
    """A rejection counts only when it fails for the expected rule."""
    output = (r.stdout or '') + (r.stderr or '')
    ok = r.returncode == 1 and code in output
    if code == 'required' or code == translate('probar_todo.cda703bd32e5'):
        ok = r.returncode == 2 and code in output
    step(name, ok, output.strip().splitlines()[-1][:70] if output.strip() else '')

@contextlib.contextmanager
def owned_temporary_directory():
    """Temporary files stay within the exclusively owned run root."""
    assert RAIZ_CORRIDA is not None
    d = RAIZ_CORRIDA / uuid.uuid4().hex[:8]
    d.mkdir(exist_ok=False)
    PROPIOS.add(d)
    try:
        yield d
    finally:
        try:
            limpiar_propio(d)
        except OSError as e:
            ERRORES_LIMPIEZA.append(f'{d}: {e}')
            raise SystemExit(1) from e

def reject_links(path: Path) -> None:
    for p in [path, *path.parents]:
        if p.is_symlink() or getattr(p, 'is_junction', lambda: False)():
            raise OSError(translate('probar_todo.9f214cf05ffb', v0=p))

def clean_owned(path: Path) -> None:
    if RAIZ_CORRIDA is None or path not in PROPIOS:
        raise OSError(translate('probar_todo.d56191f63d1e'))
    reject_links(path)
    root = RAIZ_CORRIDA.resolve()
    if not root.is_relative_to((BASE / '_tmp_pruebas').resolve()) or not path.resolve().is_relative_to(root):
        raise OSError(translate('probar_todo.773b534b418b'))
    for current, dirs, files in os.walk(path, followlinks=False):
        for name in dirs + files:
            reject_links(Path(current) / name)
    shutil.rmtree(path)
    PROPIOS.discard(path)

def run(*args: str, cwd: Path | None=None) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONNOUSERSITE='1', CRITIC_LANG=get_language())
    if RAIZ_CORRIDA is not None:
        env['TMPDIR'] = str(RAIZ_CORRIDA)
        env['TEMP'] = str(RAIZ_CORRIDA)
        env['TMP'] = str(RAIZ_CORRIDA)
    return subprocess.run([PY, '-B', *args], cwd=cwd or BASE, capture_output=True, text=True, encoding='utf-8', env=env)

def make_objection(oid: str, dims: list[str], artifact: str='PROP-PRUEBA-001', artifact_hash: str='abc') -> dict:
    return {'objection_id': oid, 'dimension': dims, 'gate': 'GATE_B', 'artifact_id': artifact, 'domain_profile': 'tech', 'timestamp': '2026-10-26T00:00:00Z', 'severity': 'major', 'claim': 'x', 'steelman': 'y', 'assumptions': [{'text': 'z', 'status': 'plausible'}], 'evidence_locator': ['a'], 'counterfactual': 'b', 'falsification': 'c', 'mitigation_vector': 'd', 'mitigation_type': 'fix', 'verification_mechanism': 'e', 'blast_radius': {'scope': 'puntual', 'impact_types': ['operativo'], 'reversible': 'trivial'}, 'time_horizon': 'corto_plazo', 'confidence': 0.8, 'provenance': {'rubric_version': '3.3.0', 'prompt_version': '3.3.0', 'model_version': 'demo', 'artifact_hash': artifact_hash}}

def make_verdict(status: str='PASA_CON_CONDICIONES', reason_code=None, with_trail: bool=True) -> dict:
    v = {'verdict_id': 'VRD-aaaaaaaaaaaa', 'artifact_id': 'PROP-PRUEBA-001', 'gate': 'GATE_B', 'timestamp': '2026-10-26T00:00:00Z', 'state_class': 'TERMINAL', 'status': status, 'reason_code': reason_code, 'suspension_control': None, 'summary_metrics': {'implicit_assumptions_discovered': 1, 'blockers_count': 0, 'majors_count': 0, 'active_accepted_risks': [], 'budget_consumed_pct': 10.0, 'suspension_cycles_reset_reason': None, 'active_skip_incidents': 0, 'skip_incident_ids': []}}
    if with_trail:
        v['audit_trail_passed_checks'] = [{'assumption': 's', 'dimension': '1', 'attack_vector': 'a', 'resistance_evidence': 'r', 'confidence': 0.9}]
    return v

def make_triage(artifact: str='PROP-PRUEBA-001', questions_resolved: bool=True, union_raw: int=5, overrides: list | None=None) -> dict:
    return {'triage_id': 'TRG-aaaaaaaaaaaa', 'artifact_id': artifact, 'timestamp': '2026-10-26T00:00:00Z', 'profiles': {'primary': 'tech', 'sub_profile': None, 'secondary': []}, 'dimensions_summary': {'total_rubric': 108, 'union_raw_count': union_raw, 'max_active_dimensions': 40, 'activated_count': 1, 'pruned_count': union_raw - 1}, 'active_dimensions': ['1'], 'pruned_families': [], 'triage_overrides': overrides if overrides is not None else [], 'previous_suspension_questions_resolved': questions_resolved, 'config_ref': 'abc'}

def run_legacy_cases() -> None:
    print('═' * 64)
    print(translate('probar_todo.8ea58ccedf72'))
    print(translate('probar_todo.6b674a2a830a'))
    print('═' * 64)
    print(translate('probar_todo.2db8119d2ea9'))
    for record_type, filename in [('objecion', 'objection.yaml'), ('triage', 'triage.yaml'), ('verdict', 'verdict.yaml'), ('outcome', 'outcome.yaml'), ('riesgo', 'risk_accepted.yaml'), ('skip', 'skip_incident.yaml'), ('patron', 'pattern.yaml')]:
        r = run(str(BASE / 'critico_cli.py'), 'validar', f'--{record_type}', f'templates/{filename}', '--borrador')
        step(translate('probar_todo.f9c4c73196fc', v0=filename), r.returncode == 0, r.stdout.strip())
    print(translate('probar_todo.6f2a8efee028'))
    with owned_temporary_directory() as tdp:
        r1 = run(str(BASE / 'critico_cli.py'), 'triage', '--artefacto', 'PROP-PRUEBA-001', '--perfil', 'business', '--sub', 'business.ecommerce', cwd=tdp)
        filename = tdp / 'triage-PROP-PRUEBA-001.yaml'
        step(translate('probar_todo.91248aa0b4ad'), r1.returncode == 0 and filename.exists())
        r2 = run(str(BASE / 'critico_cli.py'), 'triage', '--artefacto', 'PROP-PRUEBA-001', '--perfil', 'business', cwd=tdp)
        expect_rejection(translate('probar_todo.724c4b2cc909'), r2, translate('probar_todo.fd2ea5373645'))
        r3 = run(str(BASE / 'critico_cli.py'), 'triage', '--artefacto', 'X', '--perfil', 'security', cwd=tdp)
        expect_rejection(translate('probar_todo.07183a2a2775'), r3, translate('probar_todo.cda703bd32e5'))
        r4 = run(str(BASE / 'critico_cli.py'), 'plantilla', '--tipo', 'objecion', '--out', 'a.yaml', cwd=tdp)
        (tdp / 'a.yaml').write_text('x', encoding='utf-8')
        r5 = run(str(BASE / 'critico_cli.py'), 'plantilla', '--tipo', 'objecion', '--out', 'a.yaml', cwd=tdp)
        expect_rejection(translate('probar_todo.23da0b299a06'), r5, translate('probar_todo.fd2ea5373645'))
        r6 = run(str(BASE / 'critico_cli.py'), 'plantilla', '--tipo', 'objecion', '--out', 'a.yaml', '--force', cwd=tdp)
        step(translate('probar_todo.2730e48e7410'), r6.returncode == 0)
    print(translate('probar_todo.c16507e01465'))
    with owned_temporary_directory() as tdp:
        f = tdp / 'obj.yaml'
        f.write_text(yaml.safe_dump(make_objection('OBJ-abcdefabcdef', ['24', '30', '51']), allow_unicode=True), encoding='utf-8')
        r = run(str(BASE / 'critico_cli.py'), 'v1angle', '--objecion', str(f))
        step('dims 24,30,51 → v1_angle [3,8,11]', translate('probar_todo.951c9b0a216a') in r.stdout)
    print(translate('probar_todo.fa16719361d4'))
    with owned_temporary_directory() as tdp:
        vf = tdp / 'verdict.yaml'
        vf.write_text(yaml.safe_dump(make_verdict(), allow_unicode=True), encoding='utf-8')
        o1 = tdp / 'obj1.yaml'
        o2 = tdp / 'obj2.yaml'
        o1.write_text(yaml.safe_dump(make_objection('OBJ-111111111111', ['20']), allow_unicode=True), encoding='utf-8')
        o2.write_text(yaml.safe_dump(make_objection('OBJ-222222222222', ['9']), allow_unicode=True), encoding='utf-8')
        r = run(str(BASE / 'scripts' / 'outcome_runner.py'), 'init', '--verdict', str(vf), '--objeciones', str(o1), str(o2), '--horizon', 'corto_plazo', cwd=tdp)
        of = tdp / 'outcome-PROP-PRUEBA-001.yaml'
        step(translate('probar_todo.94c349d10535'), r.returncode == 0 and of.exists())
        r2 = run(str(BASE / 'scripts' / 'outcome_runner.py'), 'init', '--verdict', str(vf), cwd=tdp)
        expect_rejection(translate('probar_todo.ca41a900cf1e'), r2, translate('probar_todo.fd2ea5373645'))
        o3 = tdp / 'obj_otro_artefacto.yaml'
        o3.write_text(yaml.safe_dump(make_objection('OBJ-555555555555', ['17'], artifact='OTRO-ARTEFACTO'), allow_unicode=True), encoding='utf-8')
        other_verdict_path = tdp / 'verdict_otro.yaml'
        other_verdict = make_verdict()
        other_verdict['artifact_id'] = 'PROP-OTRO'
        other_verdict['verdict_id'] = 'VRD-999999999999'
        other_verdict_path.write_text(yaml.safe_dump(other_verdict, allow_unicode=True), encoding='utf-8')
        r_incomp = run(str(BASE / 'scripts' / 'outcome_runner.py'), 'init', '--verdict', str(other_verdict_path), '--objeciones', str(o3), cwd=tdp)
        expect_rejection(translate('probar_todo.fb49c7183062'), r_incomp, translate('probar_todo.e0951a761be7'))
        r_ign = run(str(BASE / 'scripts' / 'outcome_runner.py'), 'init', '--verdict', str(other_verdict_path), '--objeciones', str(o3), '--ignorar-incompatibles', cwd=tdp)
        other_outcome_path = tdp / 'outcome-PROP-OTRO.yaml'
        ok_ign = r_ign.returncode == 0 and other_outcome_path.exists() and (translate('probar_todo.9cf398829011') in r_ign.stdout)
        if other_outcome_path.exists():
            doc = yaml.safe_load(other_outcome_path.read_text(encoding='utf-8'))
            ok_ign = ok_ign and doc.get('seguimiento', {}).get('completo') is False and (doc['seguimiento'].get('omitidos') == ['OBJ-555555555555'])
        step(translate('probar_todo.d1b6826c1e55'), ok_ign)
        if of.exists():
            o = yaml.safe_load(of.read_text(encoding='utf-8'))
            o['outcome_id'] = 'OUT-aaaaaaaaaaaa'
            o['observed_at'] = '2026-11-26T00:00:00Z'
            o['provenance']['model_version'] = 'piloto-sintetico'
            o['provenance']['artifact_hash'] = 'abc'
            o['objection_outcomes'] = [{'objection_id': 'OBJ-111111111111', 'dimension': '20', 'profile': 'tech.code', 'materialized': 'si', 'evidence': 'falla observada', 'observed_cost': None, 'mitigacion_aplicada': True, 'propuesta_cancelada': False}, {'objection_id': 'OBJ-222222222222', 'dimension': '9', 'profile': 'tech.code', 'materialized': 'no', 'evidence': 'contrato cumplido', 'observed_cost': None, 'mitigacion_aplicada': False, 'propuesta_cancelada': False}]
            o['unpredicted_failures'] = [{'dimension': '53', 'profile': 'tech.code', 'description': 'dato viejo', 'severity': 'minor', 'evidence': 'métrica de ayer'}]
            o['calibration_sample'] = {'predicted_confidence': 0.8, 'outcome': 'si'}
            of.write_text(yaml.safe_dump(o, sort_keys=False, allow_unicode=True, width=120), encoding='utf-8')
            r_val = run(str(BASE / 'critico_cli.py'), 'validar', '--outcome', str(of))
            step(translate('probar_todo.7119f8dd430a'), r_val.returncode == 0)
            bit = tdp / 'bitacora.jsonl'
            bit.write_text(json.dumps(o, ensure_ascii=False) + '\n', encoding='utf-8')
            r4 = run(str(BASE / 'scripts' / 'outcome_runner.py'), 'metricas', '--bitacora', str(bit), '--by', 'profile')
            ok_m = r4.returncode == 0 and 'brier_score' in r4.stdout and ('intervencion_rate' in r4.stdout)
            step(translate('probar_todo.18018ec27f6f'), ok_m)
    print(translate('probar_todo.452fc2ffcc5f'))
    with owned_temporary_directory() as tdp:
        verdict_omitted = make_verdict(status='PASA', reason_code=None)
        del verdict_omitted['reason_code']
        f = tdp / 'pasa_omitido.yaml'
        f.write_text(yaml.safe_dump(verdict_omitted, allow_unicode=True), encoding='utf-8')
        r = run(str(BASE / 'critico_cli.py'), 'validar', '--verdict', str(f))
        step(translate('probar_todo.c37574913c6f'), r.returncode == 0)
        f2 = tdp / 'pasa_gate_skipped.yaml'
        f2.write_text(yaml.safe_dump(make_verdict(status='PASA', reason_code='GATE_SKIPPED'), allow_unicode=True), encoding='utf-8')
        r2 = run(str(BASE / 'critico_cli.py'), 'validar', '--verdict', str(f2))
        expect_rejection(translate('probar_todo.dd1a2cb8ef59'), r2, 'ValidationError')
        v_skip = make_verdict(status='PASA')
        v_skip['summary_metrics']['active_skip_incidents'] = 1
        f3 = tdp / 'skip_activo_pasa.yaml'
        f3.write_text(yaml.safe_dump(v_skip, allow_unicode=True), encoding='utf-8')
        r3 = run(str(BASE / 'critico_cli.py'), 'validar', '--verdict', str(f3))
        expect_rejection(translate('probar_todo.040a66c994d2'), r3, 'I3:')
        actual_artifact = tdp / 'artefacto.txt'
        empty_log = tdp / 'bitacora_vacia.jsonl'
        empty_log.write_text('', encoding='utf-8')
        tf = tdp / 'triage_otro.yaml'
        tf.write_text(yaml.safe_dump(make_triage(artifact='OTRO'), allow_unicode=True), encoding='utf-8')
        vf2 = tdp / 'verdict_prop.yaml'
        vf2.write_text(yaml.safe_dump(make_verdict(), allow_unicode=True), encoding='utf-8')
        actual_artifact.write_text('contenido', encoding='utf-8')
        r4 = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf), '--verdict', str(vf2), '--artefacto', str(actual_artifact), '--bitacora', str(empty_log))
        expect_rejection(translate('probar_todo.0f6dda24d68a'), r4, 'X1:')
        v1 = tdp / 'vacio1.yaml'
        v2 = tdp / 'vacio2.yaml'
        v1.write_text('{}\n', encoding='utf-8')
        v2.write_text('{}\n', encoding='utf-8')
        r5 = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(v1), '--verdict', str(v2), '--artefacto', str(actual_artifact), '--bitacora', str(empty_log))
        expect_rejection(translate('probar_todo.7912898450fd'), r5, 'ValidationError')
        r_sin = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf), '--verdict', str(vf2), '--bitacora', str(empty_log))
        expect_rejection(translate('probar_todo.9f85769218b5'), r_sin, 'required')
        SUSP_ID = 'SUSP-aaaaaaaaaaaa'
        hashA = hashlib.sha256('contenido A'.encode()).hexdigest()

        def verdict_suspension(vid_hex12: str, hash_at: str) -> dict:
            """Complete suspension verdict valid against its schema."""
            return {'verdict_id': 'VRD-' + vid_hex12, 'artifact_id': 'PROP-PRUEBA-001', 'gate': 'GATE_B', 'timestamp': '2026-10-26T00:00:00Z', 'state_class': 'OPERATIONAL_SUSPENSION', 'status': 'NECESITA_INFO', 'reason_code': None, 'suspension_control': {'cycle_count': 1, 'max_cycles': 2, 'timeout_hours': 48, 'target': 'author', 'suspension_reason': 'MISSING_INFO', 'missing_info_questions': ['¿versión del artefacto?'], 'unreviewed_dimensions': [], 'suspension_id': SUSP_ID, 'artifact_hash_at_suspension': hash_at}, 'summary_metrics': {'implicit_assumptions_discovered': 0, 'blockers_count': 0, 'majors_count': 0, 'active_accepted_risks': [], 'budget_consumed_pct': 10.0, 'suspension_cycles_reset_reason': None, 'active_skip_incidents': 0, 'skip_incident_ids': []}}
        v_m3 = make_verdict(status='NO_PASA', with_trail=False)
        v_m3['summary_metrics']['suspension_cycles_reset_reason'] = 'artifact_hash_change_and_questions_resolved'
        v_m3['summary_metrics']['reset_of_suspension'] = SUSP_ID
        vf3 = tdp / 'verdict_m3.yaml'
        vf3.write_text(yaml.safe_dump(v_m3, allow_unicode=True), encoding='utf-8')
        tf_m3 = tdp / 'triage_m3.yaml'
        tf_m3.write_text(yaml.safe_dump(make_triage(questions_resolved=True), allow_unicode=True), encoding='utf-8')
        suspension = verdict_suspension('aaaaaaaaaaaa', hashA)
        intermediates = [verdict_suspension('bbbbbbbbbbbb', hashlib.sha256('contenido B'.encode()).hexdigest()), verdict_suspension('cccccccccccc', hashA)]
        for r_ix in intermediates:
            r_ix['suspension_control']['suspension_id'] = 'SUSP-' + r_ix['verdict_id'][-12:]
        bit_m3 = tdp / 'bit_m3.jsonl'
        bit_m3.write_text('\n'.join((json.dumps(x, ensure_ascii=False) for x in [suspension] + intermediates)) + '\n', encoding='utf-8')
        actual_artifact.write_text('contenido C', encoding='utf-8')
        r6 = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf_m3), '--verdict', str(vf3), '--artefacto', str(actual_artifact), '--bitacora', str(bit_m3))
        step(translate('probar_todo.173690079e5e'), r6.returncode == 0, r6.stdout.strip()[:70])
        actual_artifact.write_text('contenido A', encoding='utf-8')
        r7 = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf_m3), '--verdict', str(vf3), '--artefacto', str(actual_artifact), '--bitacora', str(bit_m3))
        expect_rejection(translate('probar_todo.59f0ee01ad6c'), r7, 'M3:')
        bit_sin = tdp / 'bit_sin.jsonl'
        bit_sin.write_text('\n'.join((json.dumps(x, ensure_ascii=False) for x in intermediates)) + '\n', encoding='utf-8')
        actual_artifact.write_text('contenido C', encoding='utf-8')
        r8 = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf_m3), '--verdict', str(vf3), '--artefacto', str(actual_artifact), '--bitacora', str(bit_sin))
        expect_rejection(translate('probar_todo.74ab34dc0189'), r8, 'M3:')
        noncompliant = {'artifact_id': 'PROP-PRUEBA-001', 'suspension_control': {'suspension_id': SUSP_ID, 'artifact_hash_at_suspension': hashA}}
        bit_nc = tdp / 'bit_nc.jsonl'
        bit_nc.write_text(json.dumps(noncompliant, ensure_ascii=False) + '\n', encoding='utf-8')
        r_nc = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf_m3), '--verdict', str(vf3), '--artefacto', str(actual_artifact), '--bitacora', str(bit_nc))
        expect_rejection(translate('probar_todo.717135c45bae'), r_nc, 'M3:')
        susp_b = verdict_suspension('dddddddddddd', hashlib.sha256('contenido B'.encode()).hexdigest())
        bit_amb = tdp / 'bit_amb.jsonl'
        bit_amb.write_text('\n'.join((json.dumps(x, ensure_ascii=False) for x in [suspension, susp_b])) + '\n', encoding='utf-8')
        r_amb = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf_m3), '--verdict', str(vf3), '--artefacto', str(actual_artifact), '--bitacora', str(bit_amb))
        expect_rejection(translate('probar_todo.35a76e65b9cf'), r_amb, 'M3:')
        tf_m3.write_text(yaml.safe_dump(make_triage(questions_resolved=False), allow_unicode=True), encoding='utf-8')
        r9 = run(str(BASE / 'critico_cli.py'), 'verificar', '--triage', str(tf_m3), '--verdict', str(vf3), '--artefacto', str(actual_artifact), '--bitacora', str(bit_m3))
        expect_rejection(translate('probar_todo.e4a2f0e6a577'), r9, 'M3:')
    print(translate('probar_todo.6b6a847f5721'))
    with owned_temporary_directory() as tdp:
        evidence_file = tdp / 'evidencia.txt'
        evidence_file.write_text('contenido de la evidencia', encoding='utf-8')
        h_real = hashlib.sha256(evidence_file.read_bytes()).hexdigest()
        r_h = run(str(BASE / 'critico_cli.py'), 'hash', '--archivo', str(evidence_file))
        step(translate('probar_todo.eda623f190e0'), h_real in r_h.stdout)

        def objection_with_evidence(hash_v, source):
            o = make_objection('OBJ-777777777777', ['30'])
            item = {'source': source, 'accessed_at': '2026-10-26T00:00:00Z', 'kind': 'hecho'}
            if hash_v is not None:
                item['hash'] = hash_v
            o['evidence_detail'] = [item]
            return o
        f_ok = tdp / 'ev_ok.yaml'
        f_ok.write_text(yaml.safe_dump(objection_with_evidence(h_real, str(evidence_file)), allow_unicode=True), encoding='utf-8')
        r1 = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_ok))
        step(translate('probar_todo.7ce5192cf74e'), r1.returncode == 0 and 'HASH_VERIFICADO' in r1.stdout)
        f_bad = tdp / 'ev_bad.yaml'
        f_bad.write_text(yaml.safe_dump(objection_with_evidence('a' * 64, str(evidence_file)), allow_unicode=True), encoding='utf-8')
        r2 = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_bad))
        expect_rejection(translate('probar_todo.ccea95175387'), r2, 'RECHAZO')
        f_rem = tdp / 'ev_remota.yaml'
        f_rem.write_text(yaml.safe_dump(objection_with_evidence(None, 'https://ejemplo.com/doc'), allow_unicode=True), encoding='utf-8')
        r3 = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_rem))
        step(translate('probar_todo.6dcce33f756f'), r3.returncode == 0 and 'NO_VERIFICADO(remoto)' in r3.stdout)
        f_ina = tdp / 'ev_ina.yaml'
        f_ina.write_text(yaml.safe_dump(objection_with_evidence(h_real, str(tdp / 'no_existe.txt')), allow_unicode=True), encoding='utf-8')
        r4 = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_ina))
        step(translate('probar_todo.94e391761320'), r4.returncode == 0 and 'NO_VERIFICADO(inaccesible)' in r4.stdout)
        dir_ev = tdp / 'carpeta'
        dir_ev.mkdir()
        f_dir = tdp / 'ev_dir.yaml'
        f_dir.write_text(yaml.safe_dump(objection_with_evidence(h_real, str(dir_ev)), allow_unicode=True), encoding='utf-8')
        r_dir = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_dir))
        step(translate('probar_todo.efd39a029f32'), r_dir.returncode == 0 and 'NO_VERIFICADO(inaccesible)' in r_dir.stdout)
        f_perm = tdp / 'sin_permiso.txt'
        f_perm.write_text('x', encoding='utf-8')
        if os.name == 'posix':
            f_perm.chmod(0)
            try:
                f_perm.read_bytes()
                effective_denial = False
            except OSError:
                effective_denial = True
            if effective_denial:
                fp = tdp / 'ev_perm.yaml'
                fp.write_text(yaml.safe_dump(objection_with_evidence(h_real, str(f_perm)), allow_unicode=True), encoding='utf-8')
                r_perm = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(fp))
                step(translate('probar_todo.ebb9134a4f42'), r_perm.returncode == 0 and 'NO_VERIFICADO(inaccesible)' in r_perm.stdout)
            else:
                step(translate('probar_todo.23f6846c99d3'), None, translate('probar_todo.73206951bd8f'))
            f_perm.chmod(384)
        else:
            step(translate('probar_todo.23f6846c99d3'), None, translate('probar_todo.fcea9b47468d'))
        f_sin = tdp / 'ev_sinhash.yaml'
        f_sin.write_text(yaml.safe_dump(objection_with_evidence(None, str(evidence_file)), allow_unicode=True), encoding='utf-8')
        r5 = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_sin))
        ok5 = r5.returncode == 0 and 'NO_VERIFICADO(sin_hash)' in r5.stdout and ('HASH_VERIFICADO' not in r5.stdout.replace('NO_VERIFICADO', ''))
        step(translate('probar_todo.67d24c6b2de7'), ok5)
        o_art = make_objection('OBJ-888888888888', ['30'])
        o_art['provenance']['artifact_hash'] = 'b' * 64
        f_art = tdp / 'art_bad.yaml'
        f_art.write_text(yaml.safe_dump(o_art, allow_unicode=True), encoding='utf-8')
        r6 = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_art), '--artefacto', str(evidence_file))
        expect_rejection(translate('probar_todo.a0b7c6bb32d4'), r6, 'RECHAZO')
    print(translate('probar_todo.3fdf4379c3b7'))
    from evals.calibration import metricas_intervencion
    mi = metricas_intervencion([{'verdict_id': 'V1', 'objection_outcomes': [{'materialized': 'si', 'mitigacion_aplicada': True, 'propuesta_cancelada': False}, {'materialized': 'no', 'mitigacion_aplicada': True, 'propuesta_cancelada': False}]}, {'verdict_id': 'V2', 'objection_outcomes': [{'materialized': 'desconocido', 'mitigacion_aplicada': None, 'propuesta_cancelada': None}]}, {'verdict_id': 'V2', 'objection_outcomes': [{'materialized': 'no', 'mitigacion_aplicada': None, 'propuesta_cancelada': None}]}, {'verdict_id': 'V3', 'objection_outcomes': [{'materialized': 'si', 'mitigacion_aplicada': False, 'propuesta_cancelada': False}]}, {'verdict_id': 'V4', 'objection_outcomes': [{'materialized': 'desconocido', 'mitigacion_aplicada': None, 'propuesta_cancelada': None}]}])
    ok = mi['decisiones_observadas'] == 3 and mi['con_intervencion'] == 1 and (mi['no_observadas'] == 1) and (mi['no_informadas'] == 2) and (mi['intervencion_rate'] == round(1 / 3, 4))
    step(translate('probar_todo.513176953b93'), ok, f"rate={mi['intervencion_rate']}")
    print(translate('probar_todo.9afe0343f2b3'))
    with owned_temporary_directory() as tdp:
        f_m1 = tdp / 'm1.yaml'
        f_m1.write_text(yaml.safe_dump(make_triage(union_raw=50, overrides=[]), allow_unicode=True), encoding='utf-8')
        r_m1 = run(str(BASE / 'critico_cli.py'), 'validar', '--triage', str(f_m1))
        expect_rejection(translate('probar_todo.63708388b06a'), r_m1, 'M1:')
        only_unpredicted = {'outcome_id': 'OUT-999999999999', 'verdict_id': 'VRD-aaaaaaaaaaaa', 'artifact_id': 'A', 'horizon': 'corto_plazo', 'observed_at': '2026-11-26T00:00:00Z', 'objection_outcomes': [], 'unpredicted_failures': [{'dimension': '53', 'description': 'dato viejo', 'severity': 'minor', 'evidence': 'm'}], 'calibration_sample': None, 'provenance': {'rubric_version': '3.3.0', 'model_version': 'demo', 'artifact_hash': 'abc', 'outcome_schema_version': '3.4.0', 'observed_by': 'verificador', 'validated_by': None}}
        f_solo = tdp / 'outcome_solo.yaml'
        f_solo.write_text(yaml.safe_dump(only_unpredicted, allow_unicode=True), encoding='utf-8')
        r_solo = run(str(BASE / 'critico_cli.py'), 'validar', '--outcome', str(f_solo))
        step(translate('probar_todo.320bb0a25536'), r_solo.returncode == 0)
        empty_outcome = dict(only_unpredicted, unpredicted_failures=[])
        empty_outcome_path = tdp / 'outcome_vacio.yaml'
        empty_outcome_path.write_text(yaml.safe_dump(empty_outcome, allow_unicode=True), encoding='utf-8')
        r_vacio = run(str(BASE / 'critico_cli.py'), 'validar', '--outcome', str(empty_outcome_path))
        expect_rejection(translate('probar_todo.e4c2e9364efc'), r_vacio, 'G5:')
        contradicted_objection = make_objection('OBJ-666666666666', ['36'])
        contradicted_objection['assumptions'] = [{'text': 'supuesto roto', 'status': 'contradicted'}]
        f_contra = tdp / 'contra.yaml'
        f_contra.write_text(yaml.safe_dump(contradicted_objection, allow_unicode=True), encoding='utf-8')
        r_contra = run(str(BASE / 'critico_cli.py'), 'validar', '--objecion', str(f_contra))
        step(translate('probar_todo.88e7a0be7507'), r_contra.returncode == 0)
        src = BASE / 'evals' / 'validators.py'
        t_val = src.read_text(encoding='utf-8')
        t_val_mut = t_val.replace('    if skips > 0:', '    if skips > 0 and False:', 1)
        assert t_val_mut != t_val, translate('probar_todo.8283b405219f')
        t_val_mut = t_val_mut + '\nMUTACION_ACTIVA = True\n'
        assert t_val_mut != t_val, translate('probar_todo.a0dfd08d4f43')
        mut_dir = tdp / 'mut'
        mut_dir.mkdir()
        mut_file = mut_dir / 'validators.py'
        mut_file.write_text(t_val_mut, encoding='utf-8')
        import importlib.util
        spec = importlib.util.spec_from_file_location('validators_mut', mut_file)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            step(translate('probar_todo.69a1ad2c2991'), False, f'{e}')
            sys.exit(1)
        invalid_skip = {'artifact_id': 'A', 'status': 'PASA', 'state_class': 'TERMINAL', 'reason_code': None, 'summary_metrics': {'active_skip_incidents': 1, 'suspension_cycles_reset_reason': None}}
        original_has_i3 = any(('I3:' in v for v in __import__('evals.validators', fromlist=['x']).validar_verdict_invariantes(invalid_skip)))
        mutant_has_i3 = any(('I3:' in v for v in mod.validar_verdict_invariantes(invalid_skip)))
        step(translate('probar_todo.b0e61d04631a'), original_has_i3 and (not mutant_has_i3), '' if original_has_i3 and (not mutant_has_i3) else translate('probar_todo.9d396efd41ea'))
        mutrun = tdp / 'mutrun'
        mutrun.mkdir()
        shutil.copy2(BASE / 'critic_i18n.py', mutrun / 'critic_i18n.py')
        shutil.copytree(BASE / 'locales', mutrun / 'locales')
        (mutrun / 'critico_cli.py').write_text((BASE / 'critico_cli.py').read_text(encoding='utf-8'), encoding='utf-8')
        schema_d = mutrun / '05_schema'
        schema_d.mkdir()
        for f_schema in (BASE / '05_schema').glob('*.yaml'):
            shutil.copy2(f_schema, schema_d / f_schema.name)
        shutil.copy2(BASE / '03_rubric.yaml', mutrun / '03_rubric.yaml')
        shutil.copy2(BASE / '04_critic.config.yaml', mutrun / '04_critic.config.yaml')
        ev_d = mutrun / 'evals'
        ev_d.mkdir()
        (ev_d / '__init__.py').write_text('', encoding='utf-8')
        (ev_d / 'validators.py').write_text(t_val_mut, encoding='utf-8')
        r_carga = run('-c', "import evals.validators as v; print(v.__file__); print(getattr(v, 'MUTACION_ACTIVA', False))", cwd=mutrun)
        load_ok = r_carga.returncode == 0 and str(ev_d) in r_carga.stdout and ('True' in r_carga.stdout)
        if not load_ok:
            step(translate('probar_todo.84754a9c7087'), False, (r_carga.stdout or '') + (r_carga.stderr or ''))
            sys.exit(1)
        v_skip_m = make_verdict(status='PASA')
        v_skip_m['summary_metrics']['active_skip_incidents'] = 1
        f_skip = tdp / 'skip_activo_pasa.yaml'
        f_skip.write_text(yaml.safe_dump(v_skip_m, allow_unicode=True), encoding='utf-8')
        r_mut = run(str(mutrun / 'critico_cli.py'), 'validar', '--verdict', str(f_skip))
        mutant_accepts = r_mut.returncode == 0 and 'I3:' not in (r_mut.stdout or '') and ('ValidationError' not in (r_mut.stderr or ''))
        step(translate('probar_todo.5c2b72ca65da'), mutant_accepts, '' if mutant_accepts else translate('probar_todo.9d396efd41ea') if r_mut.returncode != 0 else translate('probar_todo.d99488ffe839'))
        broken = mut_dir / 'validators_rota.py'
        broken.write_text(t_val.replace('def validate_triage_invariants', 'def validate_triage_invariants(((', 1), encoding='utf-8')
        snippet = "import importlib.util, sys\nspec = importlib.util.spec_from_file_location('vr', sys.argv[1])\nm = importlib.util.module_from_spec(spec)\ntry:\n    spec.loader.exec_module(m)\n    print('CARGA_OK'); sys.exit(0)\nexcept Exception:\n    print('RONDA_INVALIDA: carga de la copia mutada falló — ejecución detenida (gate negativo)'); sys.exit(1)\n"
        r_gate = run('-c', snippet, str(broken))
        step(translate('probar_todo.0fa67b73d611'), r_gate.returncode == 1 and 'RONDA_INVALIDA' in r_gate.stdout)
    print(translate('probar_todo.72073deedf34'))
    for script in ['evals/calibration.py', 'evals/patterns.py', 'evals/calibration_panel.py', 'evals/validators.py']:
        r = run(str(BASE / script))
        step(script, r.returncode == 0 and 'OK' in r.stdout)
    from jsonschema import Draft202012Validator
    r = yaml.safe_load((BASE / '03_rubric.yaml').read_text(encoding='utf-8'))
    step(translate('probar_todo.3ddef3ba0fc7'), len(r['dimensions']) == 108)
    n_ok = 0
    for f in sorted((BASE / '05_schema').glob('*.yaml')):
        Draft202012Validator.check_schema(yaml.safe_load(f.read_text(encoding='utf-8')))
        n_ok += 1
    step(translate('probar_todo.b41bc3133dfc', v0=n_ok), n_ok == 8)
    r = run(str(BASE / 'scripts' / 'verify_freeze.py'))
    step(translate('probar_todo.75ae99214177'), r.returncode == 0, r.stdout.strip())

def run_closure_cases() -> None:
    """Lot regressions and a synthetic pilot, never actual human authorization."""
    import copy
    import importlib.util
    from evals.patterns import PatternStore
    from evals.calibration import brier_score
    print(translate('probar_todo.ec7f6eed3f69'))
    cli = str(BASE / 'critico_cli.py')
    runner = str(BASE / 'scripts/outcome_runner.py')
    with owned_temporary_directory() as t:

        def save_fixture(name, data):
            f = t / name
            f.write_text(yaml.safe_dump(data, allow_unicode=True), encoding='utf-8')
            return str(f)
        expect_rejection(translate('probar_todo.4f2a8f9da234'), run(cli, 'validar', '--verdict', str(BASE / 'templates/verdict.yaml')), 'ValidationError')
        v = make_verdict()
        v['timestamp'] = '2026-02-30T00:00:00Z'
        expect_rejection(translate('probar_todo.4400285b8d88'), run(cli, 'validar', '--verdict', save_fixture('fecha.yaml', v)), 'ValidationError')
        o = make_objection('OBJ-123456abcdef', ['1'])
        o['evidence_detail'] = [{'source': 'x', 'accessed_at': 'ayer', 'kind': 'hecho'}]
        expect_rejection(translate('probar_todo.2b258b7abd1d'), run(cli, 'validar', '--objecion', save_fixture('fecha-ev.yaml', o)), 'ValidationError')
        o['evidence_detail'][0].update(accessed_at='2026-10-26T00:00:00Z', kind='inventado')
        expect_rejection(translate('probar_todo.ed18e62c1b5b'), run(cli, 'validar', '--objecion', save_fixture('kind.yaml', o)), 'ValidationError')
        for field, value in [('activated_count', 2), ('pruned_count', 0)]:
            tr = make_triage()
            tr['dimensions_summary'][field] = value
            expect_rejection(translate('probar_todo.fe54c23037c2') + field, run(cli, 'validar', '--triage', save_fixture('tr.yaml', tr)), 'T1:')
        for status, state in [('NECESITA_INFO', 'TERMINAL'), ('REVISION_PARCIAL', 'TERMINAL')]:
            v = make_verdict(status=status)
            v['state_class'] = state
            f = save_fixture('estado.yaml', v)
            expect_rejection(translate('probar_todo.398d14d8168b') + status, run(cli, 'validar', '--verdict', f), 'G1:')
            expect_rejection(translate('probar_todo.2575763e2e77') + status, run(runner, 'init', '--verdict', f, cwd=t), 'G1:')
        artifact = t / 'propuesta.txt'
        artifact.write_text('Piloto sintetico: entrega sin plan de recuperacion.', encoding='utf-8')
        before = hashlib.sha256(artifact.read_bytes()).hexdigest()
        susp = make_verdict('NECESITA_INFO', with_trail=False)
        susp.update(state_class='OPERATIONAL_SUSPENSION', suspension_control={'cycle_count': 1, 'max_cycles': 2, 'timeout_hours': 24, 'target': 'author', 'suspension_id': 'SUSP-123456abcdef', 'artifact_hash_at_suspension': before, 'missing_info_questions': ['Como se recupera la entrega?'], 'suspension_reason': 'MISSING_INFO'})
        wrongstate = copy.deepcopy(susp)
        wrongstate['status'] = 'NO_PASA'
        expect_rejection(translate('probar_todo.82475038ef91'), run(cli, 'validar', '--verdict', save_fixture('susp-mal.yaml', wrongstate)), 'G1:')
        final = make_verdict()
        final['summary_metrics'].update(suspension_cycles_reset_reason='artifact_hash_change_and_questions_resolved', reset_of_suspension='SUSP-123456abcdef')
        final['verdict_id'] = 'VRD-123456abcdef'
        vf = save_fixture('final.yaml', final)
        tf = save_fixture('triage.yaml', make_triage())
        artifact.write_text('Piloto sintetico: plan de recuperacion documentado y ejercitado.', encoding='utf-8')
        bit = t / 'historia.jsonl'

        def verify_history(rows):
            bit.write_text('\n'.join((json.dumps(r) for r in rows)) + '\n', encoding='utf-8')
            return run(cli, 'verificar', '--triage', tf, '--verdict', vf, '--artefacto', str(artifact), '--bitacora', str(bit))
        invalid = copy.deepcopy(susp)
        del invalid['timestamp']
        expect_rejection(translate('probar_todo.cd09e35b73a9'), verify_history([susp, invalid]), 'M3:')
        expect_rejection(translate('probar_todo.bd2132ff7ada'), verify_history([susp, susp]), 'M3:')
        expect_rejection(translate('probar_todo.f7dfa41f835f'), verify_history([susp, []]), 'JSONL:')
        bit.write_text('{rotura', encoding='utf-8')
        expect_rejection(translate('probar_todo.18cc0e526b53'), run(cli, 'verificar', '--triage', tf, '--verdict', vf, '--artefacto', str(artifact), '--bitacora', str(bit)), 'JSONL:')
        r = verify_history([susp])
        step(translate('probar_todo.c582bb1bbf0c'), r.returncode == 0, r.stderr)
        final['summary_metrics']['suspension_cycles_reset_reason'] = None
        expect_rejection(translate('probar_todo.154a7dfca193'), run(cli, 'validar', '--verdict', save_fixture('huerfano.yaml', final)), 'M3:')
        obj = make_objection('OBJ-123456abcdef', ['1'], artifact_hash=hashlib.sha256(artifact.read_bytes()).hexdigest())
        obj.update(claim='La entrega original carecia de plan de recuperacion', steelman='Entrega con plan verificable', evidence_locator=['propuesta.txt'], falsification='Un ejercicio demuestra recuperacion', evidence_detail=[{'source': 'propuesta.txt', 'accessed_at': '2026-10-26T00:00:00Z', 'kind': 'hecho', 'hash': obj['provenance']['artifact_hash']}])
        of = save_fixture('objecion.yaml', obj)
        r = run(cli, 'validar', '--objecion', of, '--artefacto', 'propuesta.txt', cwd=BASE)
        step(translate('probar_todo.bad04686d3c5'), r.returncode == 0 and r.stdout.count('HASH_VERIFICADO') == 2)
        r = run(cli, 'validar', '--objecion', of, '--artefacto', 'ausente.txt')
        step(translate('probar_todo.37a98945c65f'), r.returncode == 0 and translate('probar_todo.56e9578de812') in r.stdout)
        r = run(runner, 'init', '--verdict', vf, '--objeciones', of, cwd=t)
        step(translate('probar_todo.e3f62dee68b6'), r.returncode == 0 and translate('probar_todo.867d9eb2dd97') in r.stdout, r.stderr)
        outcome = yaml.safe_load((t / 'outcome-PROP-PRUEBA-001.yaml').read_text(encoding='utf-8'))
        outcome.update(observed_at='2026-10-26T12:00:00Z', outcome_id='OUT-123456abcdef')
        outcome['provenance'].update(model_version='piloto-sintetico', artifact_hash=obj['provenance']['artifact_hash'])
        outcome['objection_outcomes'][0].update(materialized='no', evidence='Ejercicio sintetico de recuperacion', mitigacion_aplicada=True, propuesta_cancelada=False)
        outcome['calibration_sample'] = {'predicted_confidence': 0.2, 'outcome': 'no'}
        outpath = save_fixture('observado.yaml', outcome)
        step(translate('probar_todo.fb72facd8202'), run(runner, 'validar', '--outcome', outpath).returncode == 0)
        bitout = t / 'observados.jsonl'
        bitout.write_text(json.dumps(outcome) + '\n', encoding='utf-8')
        r = run(runner, 'metricas', '--bitacora', str(bitout), '--by', 'profile')
        step(translate('probar_todo.846209d27f56'), r.returncode == 0 and 'intervencion_rate   = 1.0' in r.stdout and ('0.0400' in r.stdout), r.stderr)
        badseg = copy.deepcopy(outcome)
        badseg['seguimiento'] = {'completo': True, 'omitidos': ['OBJ-999999999999']}
        fseg = save_fixture('seg.yaml', badseg)
        expect_rejection(translate('probar_todo.0058ef7de966'), run(cli, 'validar', '--outcome', fseg), 'S1:')
        expect_rejection(translate('probar_todo.76c2c798d4a3'), run(runner, 'validar', '--outcome', fseg), 'S1:')
        bitout.write_text(json.dumps(badseg) + '\n', encoding='utf-8')
        expect_rejection(translate('probar_todo.218630e49227'), run(runner, 'metricas', '--bitacora', str(bitout)), 'S1:')
        badseg['seguimiento'] = {}
        expect_rejection(translate('probar_todo.7e9bfac5557f'), run(cli, 'validar', '--outcome', save_fixture('seg-vacio.yaml', badseg)), 'ValidationError')
        for label, tracking in [(translate('probar_todo.b8455e81fd11'), {'completo': False, 'omitidos': []}), (translate('probar_todo.6ad696f7a5f5'), {'completo': False, 'omitidos': ['OBJ-123456abcdef']})]:
            badseg['seguimiento'] = tracking
            expect_rejection('S1: ' + label, run(cli, 'validar', '--outcome', save_fixture('seg-bad.yaml', badseg)), 'S1:')
        duplicate = copy.deepcopy(outcome)
        duplicate['objection_outcomes'] *= 2
        expect_rejection(translate('probar_todo.615c3b9d9c96'), run(cli, 'validar', '--outcome', save_fixture('dup.yaml', duplicate)), 'S1:')
        expect_rejection(translate('probar_todo.f9220b7134c5'), run(runner, 'init', '--verdict', vf, '--objeciones', of, of, cwd=t), 'S1:')
        for row in [{'predicted_confidence': 1.5, 'outcome': 'si'}, {'predicted_confidence': 0.5, 'outcome': 'desconocido'}]:
            rejected = False
            try:
                brier_score([row])
            except ValueError as e:
                rejected = 'CAL1:' in str(e)
            step(translate('probar_todo.5ffd6833aec0') + str(row), rejected)
        spec = importlib.util.spec_from_file_location('migracion_cierre', BASE / '06_migration/v2_to_v3.py')
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        legacy = make_objection('OBJ-123456abcdef', ['1'])
        legacy['blast_radius'].update(scope='local', reversible='con_plan')
        original = copy.deepcopy(legacy)
        migrated, action = migration.migrate_record(legacy)
        step(translate('probar_todo.6d2f869be118'), action == 'migrated' and legacy == original and (migrated['objection_id'] == original['objection_id']))
        again, action = migration.migrate_record(migrated)
        step(translate('probar_todo.b8738851db82'), action == 'skipped' and again == migrated)
        corrupt = copy.deepcopy(migrated)
        del corrupt['claim']
        step(translate('probar_todo.b6011d5567ed'), migration.migrate_record(corrupt)[1] == 'quarantined')
        step(translate('probar_todo.ac30d4205384'), migration.migrate_record([])[1] == 'quarantined')
        inf, outf, qf = (t / 'v2.jsonl', t / 'v3.jsonl', t / 'cuarentena.jsonl')
        inf.write_text(json.dumps(legacy) + '\n[]\n{roto\n', encoding='utf-8')
        inhash = hashlib.sha256(inf.read_bytes()).hexdigest()
        ms = str(BASE / '06_migration/v2_to_v3.py')
        r = run(ms, str(inf), str(outf), str(qf))
        step(translate('probar_todo.9661f6bf6610'), r.returncode == 1 and json.loads(r.stdout)['quarantined'] == 2 and (hashlib.sha256(inf.read_bytes()).hexdigest() == inhash))
        expect_rejection(translate('probar_todo.21b764d07716'), run(ms, str(inf), str(outf), str(qf)), translate('probar_todo.c07105db6fd2'))
        r = run(ms, str(inf), str(inf), str(qf))
        step(translate('probar_todo.617b7571cbcb'), r.returncode == 2 and translate('probar_todo.f7c51152244e') in r.stderr)
        pattern = {'pattern_id': 'PTN-123456abcdef', 'dimensions': ['1']}
        fpat = save_fixture('pat-lista.yaml', [pattern])
        step(translate('probar_todo.0e369ae01a62'), len(PatternStore.load(fpat).patterns) == 1)
        fpat = save_fixture('pat-contenedor.yaml', {'patterns': [pattern]})
        step(translate('probar_todo.c24938ac898f'), len(PatternStore.load(fpat).patterns) == 1)
        r = run('-c', "import tempfile, pathlib, os; p=pathlib.Path(tempfile.gettempdir()); print(p); print(os.environ['PYTHONDONTWRITEBYTECODE'])")
        step(translate('probar_todo.f31215bd67a4'), r.returncode == 0 and str(RAIZ_CORRIDA) in r.stdout and ('1' in r.stdout))
        snippet = "import probar_todo as p; p._main_interna=lambda:p.paso('fallo simulado',False); p.main()"
        r = run('-c', snippet)
        step(translate('probar_todo.b798e210a575'), r.returncode == 1 and translate('probar_todo.8be688adbfff') in r.stdout and ('RESULTADOS_JSON=' in r.stdout))
        snippet = "import probar_todo as p\np._main_interna=lambda:None\np._pruebas_cierre=lambda:None\nreal=p.limpiar_propio\ndef fallo(path):\n real(path)\n raise OSError('simulado despues de limpieza real')\np.limpiar_propio=fallo\np.main()"
        r = run('-c', snippet)
        step(translate('probar_todo.23062b5ed7b3'), r.returncode == 1 and translate('probar_todo.2b31b93cd4a9') in r.stderr and (translate('probar_todo.8be688adbfff') in r.stdout))
        snippet = "import probar_todo as p\nreal=p.limpiar_propio\ndef fallo(path):\n real(path)\n if path != p.RAIZ_CORRIDA: raise OSError('limpieza hija simulada')\ndef prueba():\n with p.tmp_autorizado(): pass\n print('NO_DEBE_CONTINUAR')\np.limpiar_propio=fallo\np._main_interna=prueba\np.main()"
        r = run('-c', snippet)
        step(translate('probar_todo.1526c32ca6b0'), r.returncode == 1 and translate('probar_todo.2b31b93cd4a9') in r.stderr and ('NO_DEBE_CONTINUAR' not in r.stdout))

def main() -> None:
    configure_arguments()
    global RAIZ_CORRIDA
    RESULTADOS.clear()
    ERRORES_LIMPIEZA.clear()
    RAIZ_CORRIDA = BASE / '_tmp_pruebas' / f'run-bilingual-{os.getpid()}-{uuid.uuid4().hex[:8]}'
    reject_links(RAIZ_CORRIDA.parent)
    RAIZ_CORRIDA.mkdir(parents=True)
    PROPIOS.add(RAIZ_CORRIDA)
    try:
        _main_interna()
        _pruebas_cierre()
    except SystemExit as e:
        if e.code and (not any((ok is False for _, ok, _ in RESULTADOS))):
            RESULTADOS.append((translate('probar_todo.2946fa621e44'), False, str(e.code)))
    except Exception as e:
        RESULTADOS.append((translate('probar_todo.2d88c86c6ee7'), False, str(e)))
        traceback.print_exc()
    finally:
        try:
            limpiar_propio(RAIZ_CORRIDA)
        except OSError as e:
            ERRORES_LIMPIEZA.append(f'{RAIZ_CORRIDA}: {e}')
    if ERRORES_LIMPIEZA:
        for e in ERRORES_LIMPIEZA:
            print(translate('probar_todo.cf9e7a2affb7', v0=e), file=sys.stderr)
        RESULTADOS.append((translate('probar_todo.c862c19c589e'), False, ' · '.join(ERRORES_LIMPIEZA)))
    n = sum((ok is True for _, ok, _ in RESULTADOS))
    m = sum((ok is False for _, ok, _ in RESULTADOS))
    k = sum((ok is None for _, ok, _ in RESULTADOS))
    print(translate('probar_todo.70f83be6cbad', v0=n, v1=m, v2=k, v3=len(RESULTADOS)))
    for name, ok, detail in RESULTADOS:
        if ok is None:
            print(translate('probar_todo.6d137c31ba44', v0=name, v1=detail))
    casos_serial = [{'nombre': name, 'estado': ('aprobada' if ok is True else 'fallida' if ok is False else 'no comprobable'), 'detalle': detail} for name, ok, detail in RESULTADOS]
    print('RESULTADOS_JSON=' + json.dumps({'aprobadas': n, 'fallidas': m, 'no_comprobables': k, 'total': len(RESULTADOS), 'casos': casos_serial}, ensure_ascii=False))
    sys.exit(1 if m else 0)

def paso(nombre: str, ok: bool | None, detalle: str=''):
    return step(name=nombre, ok=ok, detail=detalle)

def paso_neg(nombre: str, r: subprocess.CompletedProcess, codigo: str):
    return expect_rejection(name=nombre, r=r, code=codigo)

def tmp_autorizado():
    return owned_temporary_directory()

def sin_enlaces(path: Path):
    return reject_links(path=path)

def limpiar_propio(path: Path):
    return clean_owned(path=path)

def base_objeccion(oid: str, dims: list[str], artifact: str='PROP-PRUEBA-001', hash_artefacto: str='abc'):
    return make_objection(oid=oid, dims=dims, artifact=artifact, artifact_hash=hash_artefacto)

def base_verdict(status: str='PASA_CON_CONDICIONES', reason_code=None, con_trail: bool=True):
    return make_verdict(status=status, reason_code=reason_code, with_trail=con_trail)

def base_triage(artifact: str='PROP-PRUEBA-001', preguntas_resueltas: bool=True, union_raw: int=5, overrides: list | None=None):
    return make_triage(artifact=artifact, questions_resolved=preguntas_resueltas, union_raw=union_raw, overrides=overrides)

def _main_interna():
    return run_legacy_cases()

def _pruebas_cierre():
    return run_closure_cases()
if __name__ == '__main__':
    main()

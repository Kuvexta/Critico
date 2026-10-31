"""Check frozen rubric/config versions, all eight schema identifiers, Draft 2020-12 schema validity, the presence of BZ-109 configuration and the v3.6.0 mutations (M1/M2/M3) and the v3.5.0 sub-profile ops.cosecha (PROP-COSECHA-001). Presence does not certify an active integration."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments
import hashlib
import sys
from pathlib import Path
import yaml
try:
    from jsonschema import Draft202012Validator
except ImportError:
    print(translate('verify_freeze.55e308b1fbf4'), file=sys.stderr)
    sys.exit(2)
BASE = Path(__file__).resolve().parent.parent
EXPECTED_VALIDATORS_SHA256 = '2647125913a617d002b0db4f683ca78e8cae74c35bb7fba6beafb240c68923da'
EXPECTED_VERSIONS = {'objection.yaml': 'v3.4', 'triage.yaml': 'v3.3', 'verdict.yaml': 'v3.4', 'risk_accepted.yaml': 'v3.2', 'skip_incident.yaml': 'v3.3', 'golden_case.yaml': 'v3.3', 'outcome.yaml': 'v3.4', 'pattern.yaml': 'v3.4'}
errors: list[str] = []

def chk(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)

def main() -> int:
    r = yaml.safe_load((BASE / '03_rubric.yaml').read_text(encoding='utf-8'))
    c = yaml.safe_load((BASE / '04_critic.config.yaml').read_text(encoding='utf-8'))
    chk(r.get('frozen') is True, translate('verify_freeze.c05d61575cd8'))
    chk(c.get('frozen') is True, translate('verify_freeze.9b4922804531'))
    chk(r.get('rubric_version') == c.get('critic_version'), 'rubric_version ≠ critic_version')
    chk(c.get('critic_version') == '3.6.0', translate('verify_freeze.0deb5b294d56'))
    chk(c.get('schema_enforcement', {}).get('version') == '3.4.0', translate('verify_freeze.ac25af333c3c'))
    chk('integration' in c and 'bz109_stack_mapping' in c.get('integration', {}), translate('verify_freeze.c4bac4f3a2a6'))
    # v3.5.0 — sub-perfil ops.cosecha (PROP-COSECHA-001)
    ops_subs = c.get('profiles', {}).get('universals', {}).get('ops', {}).get('sub_profiles', {})
    chk('ops.cosecha' in ops_subs, 'sub-perfil ops.cosecha ausente del config (PROP-COSECHA-001)')
    cosecha_dims = ops_subs.get('ops.cosecha', {}).get('suggested_dimensions', [])
    chk(set(cosecha_dims) <= set(range(1, 109)), 'ops.cosecha con suggested_dimensions fuera de 1..108')
    prc = c.get('cosecha_prc', {})
    chk(prc.get('domain') == 'prc' and prc.get('sub_profile_id') == 'ops.cosecha', 'cosecha_prc sin domain prc / sub_profile_id')
    chk(prc.get('pointer_enforcement_strict') is True and prc.get('snapshot_hash_validation') is True, 'cosecha_prc sin enforcement estricto')
    chk(len(prc.get('slots', {})) == 13, 'cosecha_prc.slots ≠ 13 (C01–C13)')
    total_dims = len(r.get('dimensions', []))
    chk(total_dims == 108, translate('verify_freeze.6bbc7931b26a', v0=total_dims))
    f_val = BASE / 'evals' / 'validators.py'
    chk(f_val.exists(), translate('verify_freeze.2d7cb8060732', v0='evals/validators.py'))
    if f_val.exists():
        val_sha = hashlib.sha256(f_val.read_bytes()).hexdigest()
        chk(val_sha == EXPECTED_VALIDATORS_SHA256, translate('verify_freeze.9e1d4c2b7a8f', v0=val_sha))
    for filename, version in sorted(EXPECTED_VERSIONS.items()):
        f = BASE / '05_schema' / filename
        chk(f.exists(), translate('verify_freeze.2d7cb8060732', v0=filename))
        if not f.exists():
            continue
        s = yaml.safe_load(f.read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(s)
        chk(version in s.get('$id', ''), translate('verify_freeze.75d660135d6e', v0=filename, v1=s.get('$id'), v2=version))
    if errors:
        print('\n'.join((translate('verify_freeze.1c7f5c3461de', v0=e) for e in errors)), file=sys.stderr)
        return 1
    print(translate('verify_freeze.be965086f6ce'))
    return 0
VERSIONES_ESPERADAS = EXPECTED_VERSIONS
errores = errors
if __name__ == '__main__':
    configure_arguments()
    sys.exit(main())

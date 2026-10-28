"""Retrieve recurring failure patterns using weighted dimension and keyword Jaccard scores, with optional profile/family filters. Pattern descriptions and evidence remain original user data."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml

@dataclass
class Pattern:
    pattern_id: str
    family: str
    dimensions: list[str]
    description: str
    severity: str
    evidence: list[dict]
    count: int
    keywords: list[str] = field(default_factory=list)
    profiles: list[str] = field(default_factory=list)
    steelman: str = ''

    @classmethod
    def from_dict(cls, d: dict) -> 'Pattern':
        return cls(pattern_id=d['pattern_id'], family=d.get('family', '?'), dimensions=[str(x) for x in d.get('dimensions', [])], description=d.get('description', ''), severity=d.get('severity', 'minor'), evidence=d.get('evidence', []), count=int(d.get('count', 1)), keywords=[str(k) for k in d.get('keywords', [])], profiles=[str(p) for p in d.get('profiles', [])], steelman=d.get('steelman', ''))

class PatternStore:

    def __init__(self, patterns: list[Pattern]) -> None:
        self.patterns = patterns

    @classmethod
    def load(cls, path: str | Path) -> 'PatternStore':
        data = yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get('patterns', [])
        else:
            raise ValueError(translate('patterns.2d480149c04d'))
        if not isinstance(items, list) or any((not isinstance(p, dict) for p in items)):
            raise ValueError(translate('patterns.281dad50f709'))
        return cls([Pattern.from_dict(p) for p in items])

    def save(self, path: str | Path) -> None:
        payload = {'schema': 'pattern-store/1.0', 'patterns': [{'pattern_id': p.pattern_id, 'family': p.family, 'dimensions': p.dimensions, 'keywords': p.keywords, 'profiles': p.profiles, 'severity': p.severity, 'description': p.description, 'steelman': p.steelman, 'evidence': p.evidence, 'count': p.count} for p in self.patterns]}
        Path(path).write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=120), encoding='utf-8')

def _jaccard(a: set, b: set) -> float:
    if not a and (not b):
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

def _norm(s: str) -> str:
    s = s.lower().strip()
    s = s.replace('ñ', 'n').replace('á', 'a').replace('é', 'e')
    s = s.replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return re.sub('[^a-z0-9 ]+', '', s)

def retrieve(store: PatternStore, dimensions: list[str] | None=None, keywords: list[str] | None=None, profiles: list[str] | None=None, families: list[str] | None=None, k: int=5) -> list[dict[str, Any]]:
    """Return the top k patterns with scores, matched dimensions and citable descriptions."""
    q_dims = {str(d) for d in dimensions or []}
    q_words = {_norm(w) for w in keywords or []}
    hits: list[dict[str, Any]] = []
    for p in store.patterns:
        if families and p.family not in families:
            continue
        if profiles and (not set(profiles) & set(p.profiles)):
            continue
        d_score = _jaccard(q_dims, {str(d) for d in p.dimensions})
        p_words = {_norm(w) for w in p.keywords}
        w_score = _jaccard(q_words, p_words) if q_words else 0.0
        score = 0.7 * d_score + 0.3 * w_score
        overlap = sorted(q_dims & {str(d) for d in p.dimensions})
        if score > 0.0:
            hits.append({'pattern_id': p.pattern_id, 'score': round(score, 3), 'dimensions_matched': overlap, 'description': p.description, 'steelman': p.steelman, 'severity': p.severity, 'evidence_count': len(p.evidence), 'count': p.count})
    hits.sort(key=lambda h: (-h['score'], -h['count']))
    return hits[:k]
if __name__ == '__main__':
    configure_arguments()
    import tempfile
    store = PatternStore([Pattern(pattern_id='PTN-000000000001', family='B', dimensions=['11', '95'], keywords=['proveedor', 'espejo', 'fallback'], profiles=['business.dropshipping', 'ops.supply_chain'], severity='major', description='Dependencia de proveedor único sin espejo: falla en temporada alta', steelman='Contratar proveedor espejo con plan de activación < 24 h', evidence=[{'objection_id': 'OBJ-aaaaaaaaaaaa', 'materialized': 'si'}], count=3), Pattern(pattern_id='PTN-000000000002', family='A', dimensions=['6', '26'], keywords=['error', 'rollback'], profiles=['tech.infra'], severity='major', description='Deploy sin plan de rollback probado', steelman='Expand/contract + canary con rollback automático', evidence=[{'objection_id': 'OBJ-bbbbbbbbbbbb', 'materialized': 'no'}], count=2)])
    hits = retrieve(store, dimensions=['11', '95'], keywords=['proveedor espejo'], profiles=['business.dropshipping'], k=2)
    assert hits and hits[0]['pattern_id'] == 'PTN-000000000001'
    assert hits[0]['score'] > 0.5
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 'patterns.yaml'
        store.save(p)
        reloaded = PatternStore.load(p)
        assert len(reloaded.patterns) == 2
    print(translate('patterns.49573247296d'))
    for h in hits:
        print(' ', h)

"""Confidence calibration for the Critic (Universal Design section 15.4).

Brier score is the mean squared error between predicted confidence and observed
outcome. Group summaries and reliability bins support the calibration panel.
Wire outcome values remain si, no, parcial and desconocido."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments
from dataclasses import dataclass
import math
OUTCOME_BOOL = {'si': 1.0, 'parcial': 0.5, 'no': 0.0}

@dataclass
class CalibrationResult:
    n: int
    brier: float
    mean_confidence: float
    observed_rate: float
    overconfidence: float

    def as_dict(self) -> dict:
        return {'n': self.n, 'brier': round(self.brier, 4), 'mean_confidence': round(self.mean_confidence, 4), 'observed_rate': round(self.observed_rate, 4), 'overconfidence': round(self.overconfidence, 4)}

def _outcome_bool(outcome: str) -> float:
    if outcome not in OUTCOME_BOOL:
        raise ValueError(translate('calibration.08126f9b3e1a', v0=outcome))
    return OUTCOME_BOOL[outcome]

def _probability(value) -> float:
    p = float(value)
    if isinstance(value, bool) or not math.isfinite(p) or (not 0 <= p <= 1):
        raise ValueError(translate('calibration.f7682ac8eed7'))
    return p

def brier_score(rows: list[dict]) -> float:
    """Brier error for rows containing predicted_confidence and outcome."""
    n = 0
    total = 0.0
    for r in rows:
        p = _probability(r['predicted_confidence'])
        o = _outcome_bool(str(r['outcome']))
        total += (p - o) ** 2
        n += 1
    if n == 0:
        return 0.0
    return total / n

def calibration_summary(rows: list[dict]) -> CalibrationResult:
    """Calibration summary: Brier score and overconfidence bias."""
    n = len(rows)
    if n == 0:
        return CalibrationResult(0, 0.0, 0.0, 0.0, 0.0)
    mean_p = sum((_probability(r['predicted_confidence']) for r in rows)) / n
    obs_rate = sum((_outcome_bool(str(r['outcome'])) for r in rows)) / n
    return CalibrationResult(n=n, brier=brier_score(rows), mean_confidence=mean_p, observed_rate=obs_rate, overconfidence=mean_p - obs_rate)

def calibration_by_group(rows: list[dict], key: str) -> dict[str, dict]:
    """Aggregate calibration by any key, such as profile, dimension or severity."""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        k = str(r.get(key, 'n/a'))
        groups.setdefault(k, []).append(r)
    return {k: calibration_summary(v).as_dict() for k, v in sorted(groups.items())}

def reliability_bins(rows: list[dict], n_bins: int=5) -> list[dict]:
    """Reliability diagram: mean confidence and observed rate per bin."""
    if not rows:
        return []
    if not isinstance(n_bins, int) or n_bins <= 0:
        raise ValueError(translate('calibration.9fef12723271'))
    for row in rows:
        _probability(row['predicted_confidence'])
        _outcome_bool(row['outcome'])
    ordered = sorted(rows, key=lambda r: float(r['predicted_confidence']))
    size = max(1, round(len(ordered) / n_bins))
    bins = []
    for i in range(0, len(ordered), size):
        chunk = ordered[i:i + size]
        bins.append({'bin_confidence': round(sum((float(r['predicted_confidence']) for r in chunk)) / len(chunk), 3), 'observed_rate': round(sum((_outcome_bool(str(r['outcome'])) for r in chunk)) / len(chunk), 3), 'n': len(chunk)})
    return bins

def surprise_rate(unpredicted_count: int, decisions_count: int) -> float:
    """Unpredicted failures per decision; lower is better."""
    if decisions_count <= 0:
        return 0.0
    return unpredicted_count / decisions_count

def prediction_precision(materialized_si: int, materialized_total: int) -> float:
    """Predicted failures that occurred divided by predictions; excludes desconocido."""
    if materialized_total <= 0:
        return 0.0
    return materialized_si / materialized_total

def intervention_metrics(rows: list[dict]) -> dict:
    """Measure review intervention per unique verdict_id.

An observed decision has at least one si, no or parcial outcome.
An intervention has at least one true mitigacion_aplicada or propuesta_cancelada.
Null or missing intervention fields mean unreported, never false.
Count multiple horizons once. Report unobserved and unreported decisions separately;
exclude unobserved decisions from the rate denominator."""
    by_decision: dict[str, list[dict]] = {}
    for r in rows:
        if not isinstance(r, dict) or not isinstance(r.get('verdict_id'), str) or (not r['verdict_id']):
            raise ValueError(translate('calibration.6d6f497f5dee'))
        for item in r.get('objection_outcomes') or []:
            if item.get('materialized') not in (*OUTCOME_BOOL, 'desconocido'):
                raise ValueError(translate('calibration.eab72dcaceb6'))
            for key in ('mitigacion_aplicada', 'propuesta_cancelada'):
                if item.get(key) is not None and type(item[key]) is not bool:
                    raise ValueError(translate('calibration.847889eb1105'))
        vid = r['verdict_id']
        by_decision.setdefault(vid, []).extend(r.get('objection_outcomes') or [])
    observed_count = 0
    intervention_count = 0
    unobserved_count = 0
    unreported_count = 0
    for vid, items in by_decision.items():
        materialized_values = [i.get('materialized') for i in items]
        if any((i.get('mitigacion_aplicada') is None or i.get('propuesta_cancelada') is None for i in items)):
            unreported_count += 1
        observed = any((m in ('si', 'no', 'parcial') for m in materialized_values))
        if not observed:
            unobserved_count += 1
            continue
        observed_count += 1
        if any((i.get('mitigacion_aplicada') is True or i.get('propuesta_cancelada') is True for i in items)):
            intervention_count += 1
    rate = intervention_count / observed_count if observed_count else 0.0
    return {'intervencion_rate': round(rate, 4), 'decisiones_observadas': observed_count, 'con_intervencion': intervention_count, 'no_observadas': unobserved_count, 'no_informadas': unreported_count}
metricas_intervencion = intervention_metrics
if __name__ == '__main__':
    configure_arguments()
    rows = [{'profile': 'tech', 'predicted_confidence': 0.9, 'outcome': 'si'}, {'profile': 'tech', 'predicted_confidence': 0.9, 'outcome': 'si'}, {'profile': 'tech', 'predicted_confidence': 0.9, 'outcome': 'no'}, {'profile': 'legal', 'predicted_confidence': 0.5, 'outcome': 'si'}, {'profile': 'legal', 'predicted_confidence': 0.5, 'outcome': 'no'}]
    assert brier_score(rows) > 0
    s = calibration_summary(rows)
    assert s.n == 5 and abs(s.brier - (0.01 + 0.01 + 0.81 + 0.25 + 0.25) / 5) < 1e-09
    assert s.overconfidence > 0
    g = calibration_by_group(rows, 'profile')
    assert set(g) == {'legal', 'tech'}
    bins = reliability_bins(rows)
    assert len(bins) >= 2
    assert surprise_rate(1, 10) == 0.1
    assert prediction_precision(2, 4) == 0.5
    mi = intervention_metrics([{'verdict_id': 'V1', 'objection_outcomes': [{'materialized': 'si', 'mitigacion_aplicada': True, 'propuesta_cancelada': False}, {'materialized': 'no', 'mitigacion_aplicada': True, 'propuesta_cancelada': False}]}, {'verdict_id': 'V2', 'objection_outcomes': [{'materialized': 'desconocido', 'mitigacion_aplicada': None, 'propuesta_cancelada': None}]}, {'verdict_id': 'V2', 'objection_outcomes': [{'materialized': 'no', 'mitigacion_aplicada': None, 'propuesta_cancelada': None}]}, {'verdict_id': 'V3', 'objection_outcomes': [{'materialized': 'si', 'mitigacion_aplicada': False, 'propuesta_cancelada': False}]}, {'verdict_id': 'V4', 'objection_outcomes': [{'materialized': 'desconocido', 'mitigacion_aplicada': None, 'propuesta_cancelada': None}]}])
    assert mi['decisiones_observadas'] == 3
    assert mi['con_intervencion'] == 1
    assert mi['no_observadas'] == 1
    assert mi['no_informadas'] == 2
    assert mi['intervencion_rate'] == round(1 / 3, 4)
    print(translate('calibration.68f126739459'))
    for k, v in calibration_by_group(rows, 'profile').items():
        print(' ', k, v)

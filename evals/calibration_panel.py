"""Render calibration results as an accessible HTML fragment. Profile names are escaped; metrics and wire values are unchanged."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments
COLOR_OK = '#1a7f37'
COLOR_WARN = '#9a6700'
COLOR_BAD = '#cf222e'

def _status(overconfidence: float) -> tuple[str, str]:
    """Absolute overconfidence: <=0.10 OK, <=0.20 WARN, otherwise FAIL."""
    if abs(overconfidence) <= 0.1:
        return (COLOR_OK, 'OK')
    if abs(overconfidence) <= 0.2:
        return (COLOR_WARN, 'WARN')
    return (COLOR_BAD, 'FAIL')

def _cell(text: str, color: str | None=None) -> str:
    style = f' style="color:{color};font-weight:600;"' if color else ''
    return f'<td{style}>{text}</td>'

def calibration_section(by_profile: dict[str, dict], bins: list[dict]) -> str:
    """HTML fragment with a per-profile table and a reliability bar chart."""
    if not by_profile and (not bins):
        return ''
    rows = []
    for profile, v in by_profile.items():
        color, status = _status(v['overconfidence'])
        brier_txt = f"{v['brier']:.3f}"
        conf_txt = f"{v['mean_confidence']:.3f}"
        obs_txt = f"{v['observed_rate']:.3f}"
        overconfidence_text = f"{v['overconfidence']:+.3f}"
        rows.append(f"<tr><th scope='row'>{_esc(profile)}</th>" + _cell(str(v['n'])) + _cell(brier_txt) + _cell(conf_txt) + _cell(obs_txt) + _cell(overconfidence_text, color) + _cell(status, color) + '</tr>')
    profile_table = translate('calibration_panel.354e08df2ea2', v0=''.join(rows)) if rows else ''
    bars = []
    for b in bins:
        height = max(2, round(b['observed_rate'] * 100))
        color = COLOR_OK if abs(b['bin_confidence'] - b['observed_rate']) <= 0.1 else COLOR_BAD
        bars.append(translate('calibration_panel.50315f379c66', v0=height, v1=color, v2=b['bin_confidence'], v3=b['observed_rate'], v4=b['bin_confidence']))
    diagram = translate('calibration_panel.9e2eff6c4d2c', v0=''.join(bars)) if bars else ''
    if not profile_table and (not diagram):
        return ''
    return translate('calibration_panel.ab0fe63afaa2', v0=profile_table, v1=diagram)

def _esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def _estado(sobre: float) -> tuple[str, str]:
    return _status(overconfidence=sobre)

def _celda(texto: str, color: str | None=None) -> str:
    return _cell(text=texto, color=color)
if __name__ == '__main__':
    configure_arguments()
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from evals.calibration import calibration_by_group, reliability_bins
    rows = [{'profile': 'tech', 'predicted_confidence': 0.9, 'outcome': 'si'}, {'profile': 'tech', 'predicted_confidence': 0.9, 'outcome': 'si'}, {'profile': 'tech', 'predicted_confidence': 0.9, 'outcome': 'no'}, {'profile': 'legal', 'predicted_confidence': 0.5, 'outcome': 'si'}, {'profile': 'legal', 'predicted_confidence': 0.5, 'outcome': 'no'}]
    html = calibration_section(calibration_by_group(rows, 'profile'), reliability_bins(rows))
    assert '<section' in html and 'tech' in html and ('reliability' in html)
    assert '&lt;script' not in html
    print(translate('calibration_panel.83c34da60267'))
    print(html[:300], '...')

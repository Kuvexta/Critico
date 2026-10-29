"""Panel HTML de evals (diseño §14.1): self-contained, WCAG AA, print-friendly.

Incluye la sección de skip incidents (M-E) cuando active_skip_incidents > 0.
"""
from __future__ import annotations
from html import escape


def _bar_svg(value: float, width: int = 60) -> str:
    v = max(0.0, min(1.0, float(value or 0)))
    w = round(v * width)
    return (f'<svg width="{width + 4}" height="12" role="img" aria-label="{v:.2f}">'
            f'<rect x="2" y="1" width="{width}" height="10" fill="#eee"/>'
            f'<rect x="2" y="1" width="{w}" height="10" fill="#2a6"/></svg>')


def _banner(kind: str, text: str) -> str:
    color = {"ok": "#1a5", "warn": "#a60", "fail": "#c33"}.get(kind, "#444")
    label = {"ok": "OK", "warn": "WARN", "fail": "FAIL"}.get(kind, "INFO")
    return (f'<div class="banner banner-{kind}" role="status" style="background:{color};color:#fff;'
            f'padding:.5em 1em;font-weight:bold">{escape(label)} — {escape(text)}</div>')


def _kpi(name: str, value) -> str:
    return (f'<article class="kpi" aria-label="{escape(name)}">'
            f'<h3>{escape(name)}</h3><p class="kpi-value">{escape(str(value))}</p></article>')


def render_panel(metrics: dict, results: list[dict], dimensions: dict,
                 regression: dict | None = None) -> str:
    """Renderiza panel-evals.html completo (HTML self-contained)."""
    ms = {k: metrics.get(k, 0.0) for k in ("verdict_match_rate", "blocker_recall",
           "blocker_precision", "discovery_rate", "audit_trail_coverage",
           "implicit_assumptions_compliance", "skip_incident_rate")}
    fails = sum(1 for r in results if not r["verdict_match"])
    kind = "ok" if (fails == 0 and ms["skip_incident_rate"] == 0.0) else ("warn" if fails < len(results) else "fail")

    reg_banner = ""
    if regression:
        if regression.get("has_regression"):
            reg_banner = _banner("fail", "REGRESIÓN vs baseline: " + "; ".join(
                f"{r['metric']} ({r['current']} < {r['baseline']})" for r in regression["regressions"]))
        else:
            reg_banner = _banner("ok", "Sin regresiones vs baseline")

    skip_section = ""
    if ms["skip_incident_rate"] > 0:
        skip_section = (
            '<section id="skip-incidents" aria-label="Skip incidents">'
            '<h2>Skip incidents</h2>'
            + _banner("fail", "SKIP_INCIDENT activo ⇒ regla dura (I3): máximo NO_PASA — un artefacto con skip no puede recibir PASA")
            + '<ul>'
            + "".join(f'<li>{escape(r["case_id"])}: {r["active_skip_incidents"]} activos</li>'
                      for r in results if r["active_skip_incidents"])
            + '</ul></section>')

    rows = "".join(
        f'<tr><td>{escape(str(r["case_id"]))}</td>'
        f'<td>{"✓" if r["verdict_match"] else "✗"}</td>'
        f'<td>{len(r["blockers"]["tp"])}/{len(r["blockers"]["fn"])}/{len(r["blockers"]["fp"])}</td>'
        f'<td>{"✓" if r["audit_trail_ok"] else "✗"}</td>'
        f'<td>{r["implicit_assumptions_discovered"]}</td></tr>' for r in results)

    dim_rows = "".join(
        f'<tr><td>{escape(d)}</td><td>{v["tp"]}</td><td>{v["fn"]}</td><td>{v["fp"]}</td>'
        f'<td>{v["precision"]}</td><td>{v["recall"]}</td><td>{v["f1"]}</td>'
        f'<td>{_bar_svg(v["precision"])}</td></tr>' for d, v in dimensions.items())

    delta_rows = ""
    if regression:
        delta_rows = "".join(
            f'<tr><td>{escape(r["metric"])}</td><td>{r["current"]}</td><td>{r["baseline"]}</td>'
            f'<td>{round(float(r["current"] or 0) - float(r["baseline"] or 0), 4)}</td></tr>'
            for r in regression["regressions"]) or '<tr><td colspan="4">Sin regresiones</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Panel de evals — El Crítico</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:64rem;margin:auto;padding:1rem;color:#222;background:#fff}}
h1,h2{{color:#135}} table{{border-collapse:collapse;width:100%;margin:.5rem 0}}
th,td{{border:1px solid #999;padding:.25rem .5rem;text-align:left}}
th{{background:#eef}} .kpi{{display:inline-block;border:1px solid #999;margin:.25rem;padding:.5rem}}
.kpi-value{{font-size:1.4rem;font-weight:bold}} .banner{{margin:.5rem 0}}
@media print{{.banner{{break-inside:avoid}}}}
</style>
</head>
<body>
<h1>Panel de evals — El Crítico</h1>
{_banner(kind, f"{len(results)} casos · {fails} sin coincidencia de veredicto · skip rate {ms['skip_incident_rate']}")}
{reg_banner}
{skip_section}
<section aria-label="KPIs"><h2>KPIs</h2>
{_kpi("Verdict match", ms["verdict_match_rate"])}
{_kpi("Blocker recall", ms["blocker_recall"])}
{_kpi("Blocker precision", ms["blocker_precision"])}
{_kpi("Discovery", ms["discovery_rate"])}
{_kpi("Audit trail", ms["audit_trail_coverage"])}
{_kpi("Supuestos", ms["implicit_assumptions_compliance"])}
</section>
<section aria-label="Casos"><h2>Casos</h2>
<table><thead><tr><th>ID</th><th>Veredicto</th><th>Blockers TP/FN/FP</th><th>Trail</th><th>Supuestos</th></tr></thead>
<tbody>{rows}</tbody></table></section>
<section aria-label="Dimensiones"><h2>Dimensiones</h2>
<table><thead><tr><th>Dimensión</th><th>TP</th><th>FN</th><th>FP</th><th>P</th><th>R</th><th>F1</th><th></th></tr></thead>
<tbody>{dim_rows}</tbody></table></section>
<section aria-label="Baseline"><h2>Comparación vs baseline (Δ)</h2>
<table><thead><tr><th>Métrica</th><th>Actual</th><th>Baseline</th><th>Δ</th></tr></thead>
<tbody>{delta_rows}</tbody></table></section>
</body></html>
"""

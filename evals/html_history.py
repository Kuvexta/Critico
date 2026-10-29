"""Dashboard histórico de evals (diseño §14.2): tendencias + sparklines SVG.

M-F: skip_incident_rate entra en TREND_METRICS con flecha invertida.
"""
from __future__ import annotations
from html import escape

from evals import history as hist

ARROW = {"improving": "▲", "degrading": "▼", "stable": "="}
ARROW_LABEL = {"improving": "mejorando", "degrading": "degradando", "stable": "estable"}


def render_dashboard(history: list[dict], dimensions_trends: dict | None = None) -> str:
    """Renderiza dashboard-evals.html self-contained."""
    trends = {m: hist.trend_direction(history, m) for m in hist.TREND_METRICS}

    banner_rows = "".join(
        f'<li>{escape(m)}: {ARROW[t["direction"]]} ({ARROW_LABEL[t["direction"]]}, slope={t["slope"]})</li>'
        for m, t in trends.items())
    banner = ('<section id="tendencia" aria-label="Tendencia general"><h2>Tendencia</h2>'
              f'<ul>{banner_rows}</ul></section>')

    metric_rows = "".join(
        f'<tr><td>{escape(m)}</td><td>{t["values"][-1] if t["values"] else "—"}</td>'
        f'<td>{ARROW[t["direction"]]}</td><td>{hist.sparkline_svg(t["values"])}</td></tr>'
        for m, t in trends.items())

    dim_rows = ""
    if dimensions_trends:
        dim_rows = "".join(
            f'<tr><td>{escape(d)}</td><td>{v.get("precision", "—")}</td><td>{v.get("recall", "—")}</td>'
            f'<td>{v.get("f1", "—")}</td></tr>' for d, v in dimensions_trends.items())

    last = hist.last_n(history, 30)
    last_rows = "".join(
        f'<tr><td>{escape(h["timestamp"])}</td><td>{h["sha256"][:16]}</td>'
        f'<td>{h["metrics"].get("verdict_match_rate", 0)}</td></tr>' for h in reversed(last))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Dashboard histórico de evals — El Crítico</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:64rem;margin:auto;padding:1rem;color:#222;background:#fff}}
h1,h2{{color:#135}} table{{border-collapse:collapse;width:100%;margin:.5rem 0}}
th,td{{border:1px solid #999;padding:.25rem .5rem;text-align:left}}
th{{background:#eef}}
</style>
</head>
<body>
<h1>Dashboard histórico de evals — El Crítico</h1>
{banner}
<section aria-label="Métricas"><h2>Métricas (último valor + sparkline)</h2>
<table><thead><tr><th>Métrica</th><th>Último</th><th>Tendencia</th><th>Sparkline</th></tr></thead>
<tbody>{metric_rows}</tbody></table></section>
<section aria-label="Dimensiones"><h2>Dimensiones</h2>
<table><thead><tr><th>Dimensión</th><th>P</th><th>R</th><th>F1</th></tr></thead>
<tbody>{dim_rows}</tbody></table></section>
<section aria-label="Snapshots"><h2>Últimos 30 snapshots</h2>
<table><thead><tr><th>Timestamp</th><th>sha256</th><th>Verdict match</th></tr></thead>
<tbody>{last_rows}</tbody></table></section>
</body></html>
"""

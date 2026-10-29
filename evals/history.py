"""Historial de evaluaciones: store, tendencias y sparklines (diseño §14.2, M-F).

TREND_METRICS incluye skip_incident_rate (M-F): bajar es mejorar (flecha
invertida). Snapshots append-only en history/ con manifest.yaml anclado.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

TREND_METRICS = [
    "verdict_match_rate", "blocker_recall", "blocker_precision",
    "discovery_rate", "audit_trail_coverage",
    "implicit_assumptions_compliance", "skip_incident_rate",
]
# M-F: skip_incident_rate mejora cuando BAJA (la flecha se invierte)
LOWER_IS_BETTER = {"skip_incident_rate"}

MANIFEST_NAME = "manifest.yaml"


def snapshot(metrics: dict, history_dir: str | Path) -> dict:
    """Guarda un snapshot JSON con timestamp, sha256 y actualiza el manifest."""
    hd = Path(history_dir)
    hd.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + f"{int(time.time() * 1000) % 1000:03d}Z"
    rec = {
        "timestamp": stamp,
        "metrics": {m: metrics.get(m, 0.0) for m in TREND_METRICS},
    }
    body = json.dumps(rec, ensure_ascii=False, sort_keys=True)
    rec["sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    path = hd / f"snapshot-{stamp}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_manifest(hd)
    return rec


def load_history(history_dir: str | Path) -> list[dict]:
    hd = Path(history_dir)
    out = []
    for p in sorted(hd.glob("snapshot-*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(rec, dict) and rec.get("sha256"):
            out.append(rec)
    return out


def _slope(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return round(num / den, 6) if den else None


def trend_direction(history: list[dict], metric: str) -> dict:
    """▲ mejorando / ▼ degradando / = estable (M-F invierte la flecha)."""
    values = [h["metrics"].get(metric) for h in history if isinstance(h.get("metrics", {}).get(metric), (int, float))]
    s = _slope(values)
    if s is None or abs(s) < 1e-9:
        direction = "stable"
    else:
        improving = s < 0 if metric in LOWER_IS_BETTER else s > 0
        direction = "improving" if improving else "degrading"
    return {"metric": metric, "values": values, "slope": s, "direction": direction}


def sparkline_svg(values: list[float], width: int = 120, height: int = 30) -> str:
    """Sparkline SVG sin dependencias (polyline normalizado al rango)."""
    if not values:
        return f'<svg width="{width}" height="{height}" role="img" aria-label="sin datos"></svg>'
    if len(values) == 1:
        values = [values[0], values[0]]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    pts = []
    for i, v in enumerate(values):
        x = round(i * (width - 4) / (len(values) - 1)) + 2
        y = round(height - 2 - (v - lo) / span * (height - 4))
        pts.append(f"{x},{y}")
    return (f'<svg width="{width}" height="{height}" role="img" '
            f'aria-label="sparkline" viewBox="0 0 {width} {height}">'
            f'<polyline fill="none" stroke="#2a6" stroke-width="1.5" points="{" ".join(pts)}"/></svg>')


def update_manifest(history_dir: str | Path) -> None:
    """manifest.yaml del historial: lista de snapshots con su sha256."""
    hd = Path(history_dir)
    entries = []
    for h in load_history(hd):
        entries.append({"snapshot": f"snapshot-{h['timestamp']}.json", "sha256": h["sha256"]})
    import yaml
    (hd / MANIFEST_NAME).write_text(
        yaml.safe_dump({"algoritmo": "history-manifest-v1", "snapshots": entries},
                       allow_unicode=True, sort_keys=False), encoding="utf-8")


def last_n(history: list[dict], n: int = 30) -> list[dict]:
    return history[-n:]

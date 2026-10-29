"""History: store, tendencias y sparklines (20 tests)."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from evals import history as hist  # noqa: E402


def _m(**over) -> dict:
    d = {k: 0.5 for k in hist.TREND_METRICS}
    d.update(over)
    return d


def test_01_snapshot_crea_archivo(tmp_path):
    hist.snapshot(_m(), tmp_path)
    assert list(tmp_path.glob("snapshot-*.json"))


def test_02_snapshot_incluye_timestamp(tmp_path):
    rec = hist.snapshot(_m(), tmp_path)
    assert rec["timestamp"]


def test_03_sha256_verificable(tmp_path):
    import hashlib, json
    rec = hist.snapshot(_m(), tmp_path)
    body = json.dumps({"timestamp": rec["timestamp"], "metrics": rec["metrics"]},
                      ensure_ascii=False, sort_keys=True)
    assert rec["sha256"] == hashlib.sha256(body.encode("utf-8")).hexdigest()


def test_04_manifest_se_actualiza(tmp_path):
    hist.snapshot(_m(), tmp_path)
    import yaml
    man = yaml.safe_load((tmp_path / "manifest.yaml").read_text(encoding="utf-8"))
    assert man["algoritmo"] == "history-manifest-v1"
    assert len(man["snapshots"]) >= 1


def test_05_load_history_ordenado_por_timestamp(tmp_path):
    hist.snapshot(_m(), tmp_path)
    recs = hist.load_history(tmp_path)
    stamps = [r["timestamp"] for r in recs]
    assert stamps == sorted(stamps)


def test_06_solo_snapshots_validos_se_cargan(tmp_path):
    (tmp_path / "snapshot-20260101T000000Z.json").write_text("{\"roto\": true}", encoding="utf-8")
    assert hist.load_history(tmp_path) == []


def test_07_tendencia_mejorando():
    h = [{"metrics": {"verdict_match_rate": v}} for v in [0.5, 0.6, 0.7]]
    assert hist.trend_direction(h, "verdict_match_rate")["direction"] == "improving"


def test_08_tendencia_degradando():
    h = [{"metrics": {"verdict_match_rate": v}} for v in [0.7, 0.6, 0.5]]
    assert hist.trend_direction(h, "verdict_match_rate")["direction"] == "degrading"


def test_09_tendencia_estable():
    h = [{"metrics": {"verdict_match_rate": v}} for v in [0.5, 0.5, 0.5]]
    assert hist.trend_direction(h, "verdict_match_rate")["direction"] == "stable"


def test_10_skip_rate_baja_es_mejorar():
    h = [{"metrics": {"skip_incident_rate": v}} for v in [0.5, 0.3, 0.1]]
    assert hist.trend_direction(h, "skip_incident_rate")["direction"] == "improving"


def test_11_skip_rate_sube_es_degradar():
    h = [{"metrics": {"skip_incident_rate": v}} for v in [0.1, 0.3, 0.5]]
    assert hist.trend_direction(h, "skip_incident_rate")["direction"] == "degrading"


def test_12_sparkline_es_svg_polyline():
    svg = hist.sparkline_svg([0.1, 0.5, 0.9])
    assert "<polyline" in svg and "<svg" in svg


def test_13_sparkline_sin_datos_declara_ausencia():
    svg = hist.sparkline_svg([])
    assert "sin datos" in svg


def test_14_sparkline_con_un_solo_valor_no_rompe():
    svg = hist.sparkline_svg([0.5])
    assert "<polyline" in svg


def test_15_last_n_limita_a_30():
    h = [{"timestamp": f"t{i:02d}", "sha256": "a" * 64, "metrics": {}} for i in range(40)]
    assert len(hist.last_n(h, 30)) == 30


def test_16_trend_metrics_incluye_skip_incident_rate():
    assert "skip_incident_rate" in hist.TREND_METRICS


def test_17_lower_is_better_contiene_skip_rate():
    assert "skip_incident_rate" in hist.LOWER_IS_BETTER


def test_18_update_manifest_es_idempotente(tmp_path):
    hist.snapshot(_m(), tmp_path)
    hist.update_manifest(tmp_path)
    hist.update_manifest(tmp_path)
    import yaml
    man = yaml.safe_load((tmp_path / "manifest.yaml").read_text(encoding="utf-8"))
    assert len(man["snapshots"]) == 1


def test_19_slope_none_con_menos_de_dos_valores():
    assert hist.trend_direction([{"metrics": {"verdict_match_rate": 0.5}}],
                                "verdict_match_rate")["slope"] is None


def test_20_metricas_faltantes_se_completan_con_cero(tmp_path):
    rec = hist.snapshot({"verdict_match_rate": 0.9}, tmp_path)
    assert rec["metrics"]["skip_incident_rate"] == 0.0

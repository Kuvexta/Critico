"""R2: migración v2→v3 — idempotencia y cuarentena (10 tests)."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))
sys.path.insert(0, str(BASE / "06_migration"))

from conftest import base_objection  # noqa: E402
from v2_to_v3 import migrate_record, record_hash, migrate_file  # noqa: E402


def _v2_record(**over) -> dict:
    d = {
        "objection_id": "OBJ-" + "c" * 12,
        "propuesta": "ART-0001",
        "fecha": "2026-10-29T00:00:00Z",
        "gate": "GATE_B",
        "dimension": ["24"],
        "severity": "major",
        "claim": "afirmación bajo prueba",
        "steelman": "la versión más fuerte del reclamo",
        "assumptions": [{"text": "supuesto declarado", "status": "verified"}],
        "evidence": ["ruta/evidencia.txt"],
        "counterfactual": "qué pasaría si no se atiende",
        "falsification": "cómo se demostraría falso",
        "suggested_fix": "cómo se mitiga",
        "proposed_test": "prueba unitaria",
        "blast_radius": {"scope": "local", "reversible": "con_plan", "impact_types": ["operativo"]},
        "confidence": 0.8,
        "provenance": {"rubric_version": "3.4.0", "prompt_version": "1.0",
                       "model_version": "k-local", "artifact_hash": "e" * 64},
    }
    d.update(over)
    return d


def test_01_renombra_propuesta_a_artifact_id():
    rec, action = migrate_record(_v2_record())
    assert action == "migrated"
    assert rec["artifact_id"] == "ART-0001"
    assert "propuesta" not in rec


def test_02_renombra_fecha_a_timestamp():
    rec, _ = migrate_record(_v2_record())
    assert rec["timestamp"] == "2026-10-29T00:00:00Z"


def test_03_aplica_defaults_del_perfil_legacy():
    rec, _ = migrate_record(_v2_record())
    assert rec["domain_profile"] == "tech"
    assert rec["mitigation_type"] == "fix"
    assert rec["time_horizon"] == "corto_plazo"


def test_04_idempotencia_segunda_pasada_skipped():
    rec, _ = migrate_record(_v2_record())
    _, action2 = migrate_record(rec)
    assert action2 == "skipped"


def test_05_registra_legacy_v2_hash():
    rec, _ = migrate_record(_v2_record())
    assert rec["provenance"]["migrated_from_v2"] is True
    assert len(rec["provenance"]["legacy_v2_hash"]) == 12


def test_06_hash_deterministico_independiente_del_orden():
    a = {"x": 1, "y": 2}
    b = {"y": 2, "x": 1}
    assert record_hash(a) == record_hash(b)


def test_07_no_dict_va_a_cuarentena():
    rec, action = migrate_record("texto suelto")
    assert action == "quarantined"


def test_08_record_invalido_va_a_cuarentena():
    bad = _v2_record(claim=None)
    rec, action = migrate_record(bad)
    assert action == "quarantined"


def test_09_migrate_file_cuenta_y_cuarentena(tmp_path):
    inp = tmp_path / "in.jsonl"
    out = tmp_path / "out.jsonl"
    q = tmp_path / "q.jsonl"
    inp.write_text(json.dumps(_v2_record()) + "\n" + "no es json\n", encoding="utf-8")
    counts = migrate_file(str(inp), str(out), str(q))
    assert counts == {"migrated": 1, "skipped": 0, "quarantined": 1, "total": 2}
    assert out.read_text(encoding="utf-8").strip()
    assert q.read_text(encoding="utf-8").strip()


def test_10_scope_y_reversible_mapeados():
    rec, _ = migrate_record(_v2_record(blast_radius={"scope": "servicio", "reversible": "irreversible",
                                                      "impact_types": ["operativo"]}))
    assert rec["blast_radius"]["scope"] == "sistema_completo"
    assert rec["blast_radius"]["reversible"] == "irreversible"

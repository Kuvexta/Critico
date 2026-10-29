"""Builders compartidos de la suite de 153 (materializada de la especificación)."""
from __future__ import annotations
import sys
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

SCHEMAS = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in (BASE / "05_schema").glob("*.yaml")}


def base_triage(**over) -> dict:
    d = {
        "triage_id": "TRG-" + "a" * 12,
        "artifact_id": "ART-0001",
        "timestamp": "2026-10-29T00:00:00Z",
        "profiles": {"primary": "tech", "sub_profile": None, "secondary": []},
        "dimensions_summary": {"total_rubric": 108, "union_raw_count": 3,
                               "max_active_dimensions": 40, "activated_count": 2, "pruned_count": 1},
        "active_dimensions": ["24", "30"],
        "pruned_families": ["A"],
        "triage_overrides": [],
        "triage_split_recommendation": None,
        "previous_suspension_questions_resolved": False,
        "config_ref": "d" * 64,
    }
    d.update(over)
    return d


def base_verdict(**over) -> dict:
    d = {
        "verdict_id": "VRD-" + "b" * 12,
        "artifact_id": "ART-0001",
        "gate": "GATE_B",
        "timestamp": "2026-10-29T00:00:00Z",
        "state_class": "TERMINAL",
        "status": "PASA",
        "reason_code": None,
        "suspension_control": None,
        "audit_trail_passed_checks": [
            {"assumption": "soporta carga", "dimension": "24", "attack_vector": "pico de tráfico",
             "resistance_evidence": "prueba de carga OK", "confidence": 0.9},
        ],
        "summary_metrics": {"implicit_assumptions_discovered": 2, "blockers_count": 0,
                            "majors_count": 0, "active_accepted_risks": [],
                            "budget_consumed_pct": 10.0, "suspension_cycles_reset_reason": None,
                            "active_skip_incidents": 0, "skip_incident_ids": []},
    }
    d.update(over)
    return d


def base_objection(**over) -> dict:
    d = {
        "objection_id": "OBJ-" + "c" * 12,
        "gate": "GATE_B",
        "artifact_id": "ART-0001",
        "domain_profile": "tech",
        "timestamp": "2026-10-29T00:00:00Z",
        "dimension": ["24"],
        "severity": "major",
        "claim": "afirmación bajo prueba",
        "steelman": "la versión más fuerte del reclamo",
        "assumptions": [{"text": "supuesto declarado", "status": "verified"}],
        "evidence_locator": ["ruta/evidencia.txt"],
        "counterfactual": "qué pasaría si no se atiende",
        "falsification": "cómo se demostraría falso",
        "mitigation_vector": "cómo se mitiga",
        "mitigation_type": "fix",
        "verification_mechanism": "prueba unitaria",
        "blast_radius": {"scope": "puntual", "reversible": "con_plan_y_costo", "impact_types": ["operativo"]},
        "time_horizon": "corto_plazo",
        "confidence": 0.8,
        "provenance": {"rubric_version": "3.4.0", "prompt_version": "1.0",
                       "model_version": "k-local", "artifact_hash": "e" * 64},
    }
    d.update(over)
    return d


def base_risk_accepted(**over) -> dict:
    d = {
        "objection_id": "OBJ-" + "f" * 12,
        "status": "RISK_ACCEPTED_BY_GATE_C",
        "accepted_by": "GATE_C",
        "date": "2026-10-29T00:00:00Z",
        "expiration_date": "2026-11-29T00:00:00Z",
        "context_condition": {"qualitative_trigger": "umbral cualitativo"},
        "rationale": "riesgo aceptado por Dirección",
        "flag": None,
        "provenance": {"verdict_id": "VRD-" + "b" * 12, "artifact_hash": "e" * 64},
    }
    d.update(over)
    return d

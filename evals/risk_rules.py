"""Regla R4 (riesgo aceptado): sin fingir evaluación cuantitativa.

Módulo NO congelado: la regla vive aquí para no tocar evals/validators.py
(frozen por CAMBIO-16). Su cableado al pipeline validate_record es candidata
de CAMBIO (backlog) — mientras tanto la suite la ejercita directamente.
"""
from __future__ import annotations
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from critic_i18n import translate  # noqa: E402


def validate_risk_accepted_invariants(rec: dict) -> list[str]:
    """R4: metric_source unavailable ⇒ solo qualitative_trigger + flag explícito."""
    errors: list[str] = []
    cc = rec.get("context_condition") or {}
    qt = cc.get("quantitative_threshold")
    source = (qt or {}).get("metric_source") if isinstance(qt, dict) else None
    if source == "unavailable":
        if rec.get("flag") != "QUANTITATIVE_UNAVAILABLE":
            errors.append(translate("validators.r4_flag_faltante"))
    elif qt is not None and qt.get("metric_source") is None:
        errors.append(translate("validators.r4_sin_source"))
    return errors

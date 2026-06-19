"""Negotiation Agent (\u03c3\u00b2 consensus) + Dynamic Alerting Index (I_alert)."""
from __future__ import annotations

import statistics
import uuid
from datetime import datetime, timezone
from typing import Any

THETA_SAFE = 0.04  # variance threshold (~0.2 std on [0,1])


def negotiation_agent(
    chem: dict[str, Any], phys: dict[str, Any], psych: dict[str, Any]
) -> dict[str, Any]:
    scores = [chem["score"], phys["score"], psych["score"]]
    confs = [chem["confidence"], phys["confidence"], psych["confidence"]]
    mean_score = statistics.fmean(scores)
    sigma_sq = statistics.pvariance(scores)
    mean_conf = statistics.fmean(confs)
    validation_flag = sigma_sq > THETA_SAFE or mean_conf < 0.4

    deviations = {
        "Chemical": abs(chem["score"] - mean_score),
        "Physical": abs(phys["score"] - mean_score),
        "Psychological": abs(psych["score"] - mean_score),
    }
    outlier = max(deviations, key=deviations.get)

    context_memo: dict[str, Any] | None = None
    if validation_flag:
        context_memo = {
            "memo_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reason": (
                f"Consensus variance \u03c3\u00b2={sigma_sq:.4f} exceeds \u03b8_safe={THETA_SAFE}"
                if sigma_sq > THETA_SAFE
                else f"Mean confidence {mean_conf:.2f} below 0.40 threshold"
            ),
            "outlier_agent": outlier,
            "summary": (
                f"Chemical={chem['score']:.2f} (conf {chem['confidence']:.2f}), "
                f"Physical={phys['score']:.2f} (conf {phys['confidence']:.2f}), "
                f"Psychological={psych['score']:.2f} (conf {psych['confidence']:.2f}). "
                f"Divergence detected \u2014 escalate for human-in-the-loop review."
            ),
            "agent_findings": {
                "Chemical": chem["key_findings"],
                "Physical": phys["key_findings"],
                "Psychological": psych["key_findings"],
            },
            "status": "pending_clinician_review",
        }

    return {
        "consensus_score": round(mean_score, 4),
        "sigma_sq": round(sigma_sq, 6),
        "mean_confidence": round(mean_conf, 4),
        "theta_safe": THETA_SAFE,
        "validation_flag": validation_flag,
        "outlier_agent": outlier,
        "context_memo": context_memo,
    }


def _norm(v: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    return max(0.0, min(1.0, (v - lo) / (hi - lo)))


def dynamic_alert_index(
    consensus_score: float,
    vas_pain: float = 0,
    bpi_interference: float = 0,
    dram_distress: float = 0,
    rom_deficit_pct: float = 0,
    snfl_pg_per_ml: float = 0,
) -> dict[str, Any]:
    components = {
        "consensus": consensus_score,
        "vas_pain": _norm(vas_pain, 0, 10),
        "bpi_interference": _norm(bpi_interference, 0, 10),
        "dram_distress": _norm(dram_distress, 0, 100),
        "rom_deficit": _norm(rom_deficit_pct, 0, 60),
        "snfl_elevation": _norm(snfl_pg_per_ml, 5, 40),
    }
    weights = {
        "consensus": 0.40,
        "vas_pain": 0.15,
        "bpi_interference": 0.15,
        "dram_distress": 0.10,
        "rom_deficit": 0.10,
        "snfl_elevation": 0.10,
    }
    i_alert = round(sum(components[k] * weights[k] for k in weights), 4)
    base = 0.40
    red = round(base * 1.4, 4)

    if i_alert >= red:
        tier, actions = "RED", [
            "Pause VR training",
            "Lock write-access to therapy plan",
            "Trigger synchronous clinician triage",
        ]
    elif i_alert >= base:
        tier, actions = "YELLOW", [
            "Modify VR intensity (reduce by 30%)",
            "Deliver targeted digital pain-neuroscience education",
            "Increase EMA polling frequency",
        ]
    else:
        tier, actions = "GREEN", [
            "Maintain current therapy path",
            "Log background metrics",
            "Continue scheduled EMA cadence",
        ]

    return {
        "i_alert": i_alert,
        "tier": tier,
        "threshold_base": base,
        "threshold_red": red,
        "components": {k: round(v, 4) for k, v in components.items()},
        "weights": weights,
        "recommended_actions": actions,
    }

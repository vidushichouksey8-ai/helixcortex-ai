"""Pytest suite for HelixCortex POC core math (no LLM calls)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from poc_core_flow import (  # noqa: E402
    THETA_SAFE,
    build_fhir_bundle,
    dynamic_alert_index,
    negotiation_agent,
    validate_fhir_bundle,
)


def _mk(score, conf=0.8, findings=None):
    return {
        "score": score,
        "confidence": conf,
        "narrative": "test",
        "key_findings": findings or ["f1"],
    }


def test_negotiation_agreement_no_flag():
    res = negotiation_agent(_mk(0.5), _mk(0.55), _mk(0.5))
    assert res["sigma_sq"] < THETA_SAFE
    assert res["validation_flag"] is False
    assert res["context_memo"] is None


def test_negotiation_divergence_triggers_memo():
    res = negotiation_agent(_mk(0.1), _mk(0.9), _mk(0.5))
    assert res["sigma_sq"] > THETA_SAFE
    assert res["validation_flag"] is True
    assert res["context_memo"]["status"] == "pending_clinician_review"


def test_negotiation_low_confidence_triggers_flag():
    res = negotiation_agent(_mk(0.5, 0.2), _mk(0.5, 0.2), _mk(0.5, 0.2))
    assert res["validation_flag"] is True


def test_alert_tier_green():
    res = dynamic_alert_index(0.1, 1.0, 1.0, 10, 5, 6.0)
    assert res["tier"] == "GREEN"


def test_alert_tier_yellow():
    res = dynamic_alert_index(0.55, 5.0, 5.0, 50, 25, 18.0)
    assert res["tier"] == "YELLOW"


def test_alert_tier_red_1_4x_rule():
    res = dynamic_alert_index(0.9, 9.0, 9.0, 90, 50, 38.0)
    assert res["tier"] == "RED"
    assert res["threshold_red"] == round(0.40 * 1.4, 4)


def test_alert_actions_present():
    for cs in [0.1, 0.5, 0.9]:
        res = dynamic_alert_index(cs, 5, 5, 50, 25, 18)
        assert len(res["recommended_actions"]) >= 2


def test_fhir_bundle_valid():
    patient = {"name": "Test", "gender": "female", "birth_date": "1990-01-01"}
    biomarkers = {"sNfL_pg_per_ml": 20.0, "IL6_pg_per_ml": 8.0, "TNFa_pg_per_ml": 12.0}
    psych = {"vas_pain": 6, "bpi_interference": 5, "dram_distress": 60}
    kin = {"hrv_rmssd_ms": 25.0, "rom_deficit_pct": 30}
    assessment = {
        "negotiation": {"sigma_sq": 0.001, "validation_flag": False},
        "alert": {"tier": "YELLOW", "i_alert": 0.5},
    }
    bundle = build_fhir_bundle(patient, biomarkers, psych, kin, assessment)
    val = validate_fhir_bundle(bundle)
    assert val["valid"] is True, val["errors"]
    assert "Patient" in val["resource_types"]
    assert "Observation" in val["resource_types"]
    assert "DiagnosticReport" in val["resource_types"]


def test_fhir_validation_catches_errors():
    bad = {"resourceType": "Bundle", "type": "collection", "entry": []}
    val = validate_fhir_bundle(bad)
    assert val["valid"] is False
    assert any("empty" in e for e in val["errors"])


def test_alert_score_bounds():
    res = dynamic_alert_index(1.0, 10, 10, 100, 60, 40)
    assert 0 <= res["i_alert"] <= 1
    res2 = dynamic_alert_index(0.0, 0, 0, 0, 0, 0)
    assert res2["i_alert"] == 0.0

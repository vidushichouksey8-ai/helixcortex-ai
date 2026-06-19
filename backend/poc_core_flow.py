"""
HelixCortex Labs — Phase 1 POC

Validates in ONE script:
  1. Emergent LLM Key integration for 3 specialist agents (Chemical / Physical / Psychological)
     returning STRICT JSON outputs.
  2. Negotiation Agent — consensus variance σ² + Context Memo generation.
  3. Dynamic Alerting Index (I_alert) tier classification: GREEN / YELLOW / RED (1.4× rule).
  4. FHIR R4 payload generation + basic structural validation.

Run: `python poc_core_flow.py` from /app/backend
"""

import asyncio
import json
import os
import re
import statistics
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env at /app/backend/.env
load_dotenv(Path(__file__).resolve().parent / ".env")

from emergentintegrations.llm.chat import LlmChat, UserMessage  # noqa: E402

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
if not EMERGENT_LLM_KEY:
    print("FATAL: EMERGENT_LLM_KEY missing from /app/backend/.env")
    sys.exit(1)

LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-sonnet-4-6"  # medical reasoning, JSON friendly

# ---------------------------------------------------------------------------
# Reference clinical ranges (for grounding LLM and computing fallbacks)
# ---------------------------------------------------------------------------
CLINICAL_REFS = {
    "sNfL_pg_per_ml": {"healthy_max": 10.0, "elevated": 20.0, "high": 35.0},
    "gamma_ratio": {"healthy": 1.0, "elevated": 1.5, "high": 2.0},  # Glu/GABA
    "IL6_pg_per_ml": {"normal_max": 5.0, "elevated": 10.0},
    "TNFa_pg_per_ml": {"normal_max": 8.0, "elevated": 15.0},
    "IL1b_pg_per_ml": {"normal_max": 3.0, "elevated": 6.0},
    "substance_p_pg_per_ml": {"normal_max": 50.0, "elevated": 100.0},
    "BDNF_ng_per_ml": {"normal": 20.0, "elevated_low": 10.0},
    "HRV_rmssd_ms": {"healthy_min": 35.0, "low": 20.0},
    "ROM_deficit_pct": {"mild": 10, "moderate": 25, "severe": 40},
    "VAS_pain": {"min": 0, "max": 10, "high": 7},
    "BPI_interference": {"min": 0, "max": 10},
    "DRAM_distress": {"min": 0, "max": 100, "high": 60},
}

# ---------------------------------------------------------------------------
# JSON output schema enforced for all agents
# ---------------------------------------------------------------------------
AGENT_SCHEMA = {
    "score": "float in [0,1] — agent's sensitization/distress score",
    "confidence": "float in [0,1] — confidence in the score",
    "narrative": "1-3 sentence clinical narrative",
    "key_findings": "list[str] of 2-5 concise findings",
}

SYSTEM_BASE = (
    "You are a specialist clinical AI agent in the HelixCortex Labs decoupled "
    "multi-agent diagnostic platform for nociplastic pain (fibromyalgia, chronic "
    "spine pain). You ONLY output a JSON object with keys: score (0-1 float), "
    "confidence (0-1 float), narrative (string), key_findings (array of strings). "
    "Never include code fences or commentary outside the JSON."
)


def _extract_json(text: str) -> dict[str, Any]:
    """Robust JSON extraction (handles code fences and stray prose)."""
    if not text:
        raise ValueError("empty LLM response")
    # Strip code fences
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    # Find first {...} block
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"no JSON object found in: {text[:200]}")
    return json.loads(cleaned[start : end + 1])


def _coerce_agent_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate + clamp agent output to schema."""
    score = float(raw.get("score", 0.0))
    confidence = float(raw.get("confidence", 0.5))
    narrative = str(raw.get("narrative", "")).strip() or "No narrative provided."
    findings = raw.get("key_findings", []) or []
    if isinstance(findings, str):
        findings = [findings]
    findings = [str(f) for f in findings][:6]
    return {
        "score": max(0.0, min(1.0, score)),
        "confidence": max(0.0, min(1.0, confidence)),
        "narrative": narrative,
        "key_findings": findings,
    }


async def _call_agent(agent_name: str, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Call Emergent LLM with structured output and retry."""
    user_text = (
        f"Analyze the following patient payload as the {agent_name}. "
        f"Reference ranges: {json.dumps(CLINICAL_REFS)}. "
        f"PAYLOAD:\n{json.dumps(payload, indent=2)}\n\n"
        f"Respond ONLY with JSON matching: {json.dumps(AGENT_SCHEMA)}"
    )

    last_err: Exception | None = None
    for attempt in range(2):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"poc-{agent_name}-{uuid.uuid4()}",
                system_message=system_prompt,
            ).with_model(LLM_PROVIDER, LLM_MODEL)
            resp = await chat.send_message(UserMessage(text=user_text))
            text = resp if isinstance(resp, str) else getattr(resp, "content", str(resp))
            return _coerce_agent_output(_extract_json(text))
        except Exception as e:  # noqa: BLE001
            last_err = e
            await asyncio.sleep(0.5)

    # Deterministic fallback so the pipeline keeps running
    print(f"[WARN] {agent_name} LLM failed after retries ({last_err}); using fallback")
    return {
        "score": 0.5,
        "confidence": 0.2,
        "narrative": f"{agent_name} fallback: LLM unavailable, manual review required.",
        "key_findings": ["llm_unavailable", "manual_review_required"],
    }


# ---------------------------------------------------------------------------
# Specialist agents
# ---------------------------------------------------------------------------
async def chemical_agent(biomarkers: dict[str, Any]) -> dict[str, Any]:
    sys_msg = (
        SYSTEM_BASE
        + " You are the Chemical Agent. Evaluate systemic neuroinflammation and "
        "neurotoxicity from biomarkers: sNfL (axonal stress), gamma_ratio "
        "(Glutamate/GABA balance), pro-inflammatory cytokines (IL-1β, IL-6, TNF-α), "
        "Substance P, BDNF. Higher dysregulation → higher score."
    )
    return await _call_agent("Chemical Agent", sys_msg, biomarkers)


async def physical_agent(kinematics: dict[str, Any]) -> dict[str, Any]:
    sys_msg = (
        SYSTEM_BASE
        + " You are the Physical Agent. Evaluate kinetic sensitization from VR "
        "kinematics: joint coordinates, velocity vectors, range-of-motion deficits, "
        "guarding behaviors, HRV rmssd, sleep efficiency. Higher dysfunction → "
        "higher score."
    )
    return await _call_agent("Physical Agent", sys_msg, kinematics)


async def psychological_agent(psych_payload: dict[str, Any]) -> dict[str, Any]:
    sys_msg = (
        SYSTEM_BASE
        + " You are the Psychological Agent. Use NLP-style reasoning to identify "
        "pain catastrophizing, kinesiophobia, anxiety, 'brain fog' from patient "
        "text/EMA scales (BPI interference, DRAM distress, VAS pain). Higher "
        "distress → higher score."
    )
    return await _call_agent("Psychological Agent", sys_msg, psych_payload)


# ---------------------------------------------------------------------------
# Negotiation Agent (σ² consensus + Context Memo)
# ---------------------------------------------------------------------------
THETA_SAFE = 0.04  # variance threshold (~0.2 std dev on a [0,1] scale)


def negotiation_agent(
    chem: dict[str, Any], phys: dict[str, Any], psych: dict[str, Any]
) -> dict[str, Any]:
    scores = [chem["score"], phys["score"], psych["score"]]
    confidences = [chem["confidence"], phys["confidence"], psych["confidence"]]

    mean_score = statistics.fmean(scores)
    sigma_sq = statistics.pvariance(scores)  # population variance
    mean_conf = statistics.fmean(confidences)

    validation_flag = sigma_sq > THETA_SAFE or mean_conf < 0.4

    # Identify outlier agent (largest absolute deviation from mean)
    deviations = {
        "Chemical": abs(chem["score"] - mean_score),
        "Physical": abs(phys["score"] - mean_score),
        "Psychological": abs(psych["score"] - mean_score),
    }
    outlier = max(deviations, key=deviations.get)

    context_memo = None
    if validation_flag:
        context_memo = {
            "memo_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reason": (
                f"Consensus variance σ²={sigma_sq:.4f} exceeds θ_safe={THETA_SAFE}"
                if sigma_sq > THETA_SAFE
                else f"Mean confidence {mean_conf:.2f} below 0.40 threshold"
            ),
            "outlier_agent": outlier,
            "summary": (
                f"Chemical={chem['score']:.2f} (conf {chem['confidence']:.2f}), "
                f"Physical={phys['score']:.2f} (conf {phys['confidence']:.2f}), "
                f"Psychological={psych['score']:.2f} (conf {psych['confidence']:.2f}). "
                f"Divergence detected — escalate for human-in-the-loop review."
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


# ---------------------------------------------------------------------------
# Dynamic Alerting Index I_alert
# ---------------------------------------------------------------------------
def _norm(value: float, low: float, high: float) -> float:
    if high == low:
        return 0.0
    return max(0.0, min(1.0, (value - low) / (high - low)))


def dynamic_alert_index(
    consensus_score: float,
    vas_pain: float,
    bpi_interference: float,
    dram_distress: float,
    rom_deficit_pct: float,
    snfl_pg_per_ml: float,
) -> dict[str, Any]:
    """
    Composite risk score 0-1 from:
      - consensus_score (40%)
      - VAS pain (15%)
      - BPI functional interference (15%)
      - DRAM psychometric distress (10%)
      - ROM deficit (10%)
      - sNfL elevation (10%)
    Tier:
      GREEN < 0.40
      YELLOW 0.40 - 0.56 (below 1.4× of 0.40)
      RED   >= 0.56  (1.4× threshold)
    """
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
    i_alert = sum(components[k] * weights[k] for k in weights)
    i_alert = round(i_alert, 4)

    base_threshold = 0.40
    red_threshold = round(base_threshold * 1.4, 4)  # 0.56

    if i_alert >= red_threshold:
        tier = "RED"
        actions = [
            "Pause VR training",
            "Lock write-access to therapy plan",
            "Trigger synchronous clinician triage",
        ]
    elif i_alert >= base_threshold:
        tier = "YELLOW"
        actions = [
            "Modify VR intensity (reduce by 30%)",
            "Deliver targeted digital pain-neuroscience education",
            "Increase EMA polling frequency",
        ]
    else:
        tier = "GREEN"
        actions = [
            "Maintain current therapy path",
            "Log background metrics",
            "Continue scheduled EMA cadence",
        ]

    return {
        "i_alert": i_alert,
        "tier": tier,
        "threshold_base": base_threshold,
        "threshold_red": red_threshold,
        "components": {k: round(v, 4) for k, v in components.items()},
        "weights": weights,
        "recommended_actions": actions,
    }


# ---------------------------------------------------------------------------
# FHIR R4 mapping
# ---------------------------------------------------------------------------
LOINC = {
    "sNfL": ("82293-6", "Neurofilament light chain [Mass/volume] in Serum or Plasma"),
    "glutamate": ("14749-6", "Glutamate [Mass/volume] in Serum"),
    "gaba": ("LP38458-1", "Gamma-aminobutyric acid"),
    "IL6": ("26881-3", "Interleukin 6 [Mass/volume] in Serum or Plasma"),
    "TNFa": ("57835-4", "Tumor necrosis factor alpha [Mass/volume]"),
    "VAS_pain": ("72514-3", "Pain severity - 0-10 verbal numeric rating"),
    "BPI": ("75441-6", "Brief pain inventory short form"),
    "HRV_rmssd": ("80404-9", "Heart rate variability - RMSSD"),
}
SNOMED = {
    "fibromyalgia": ("203082005", "Fibromyalgia"),
    "nociplastic_pain": ("279045009", "Chronic pain"),
    "central_sensitization": ("309253009", "Central sensitization"),
    "kinesiophobia": ("285852003", "Fear of movement"),
}


def build_fhir_bundle(
    patient: dict[str, Any],
    biomarkers: dict[str, Any],
    psych_payload: dict[str, Any],
    kinematics: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    patient_id = patient.get("id") or str(uuid.uuid4())

    entries: list[dict[str, Any]] = []

    # Patient
    entries.append(
        {
            "resource": {
                "resourceType": "Patient",
                "id": patient_id,
                "name": [{"text": patient.get("name", "Unknown Patient")}],
                "gender": patient.get("gender", "unknown"),
                "birthDate": patient.get("birth_date", "1980-01-01"),
            }
        }
    )

    def obs(loinc_key: str, value: float, unit: str) -> dict[str, Any]:
        code, display = LOINC[loinc_key]
        return {
            "resource": {
                "resourceType": "Observation",
                "id": str(uuid.uuid4()),
                "status": "final",
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": code, "display": display}
                    ]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": now,
                "valueQuantity": {"value": value, "unit": unit},
            }
        }

    if "sNfL_pg_per_ml" in biomarkers:
        entries.append(obs("sNfL", biomarkers["sNfL_pg_per_ml"], "pg/mL"))
    if "IL6_pg_per_ml" in biomarkers:
        entries.append(obs("IL6", biomarkers["IL6_pg_per_ml"], "pg/mL"))
    if "TNFa_pg_per_ml" in biomarkers:
        entries.append(obs("TNFa", biomarkers["TNFa_pg_per_ml"], "pg/mL"))
    if "vas_pain" in psych_payload:
        entries.append(obs("VAS_pain", psych_payload["vas_pain"], "{score}"))
    if "bpi_interference" in psych_payload:
        entries.append(obs("BPI", psych_payload["bpi_interference"], "{score}"))
    if "hrv_rmssd_ms" in kinematics:
        entries.append(obs("HRV_rmssd", kinematics["hrv_rmssd_ms"], "ms"))

    # Diagnostic Report
    snomed_code, snomed_display = SNOMED["nociplastic_pain"]
    entries.append(
        {
            "resource": {
                "resourceType": "DiagnosticReport",
                "id": str(uuid.uuid4()),
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": snomed_code,
                            "display": snomed_display,
                        }
                    ]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": now,
                "conclusion": (
                    f"HelixCortex multi-agent assessment — Tier {assessment['alert']['tier']}, "
                    f"I_alert={assessment['alert']['i_alert']}, "
                    f"σ²={assessment['negotiation']['sigma_sq']}, "
                    f"validation_flag={assessment['negotiation']['validation_flag']}."
                ),
            }
        }
    )

    bundle = {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "collection",
        "timestamp": now,
        "entry": entries,
    }
    return bundle


def validate_fhir_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if bundle.get("resourceType") != "Bundle":
        errors.append("missing/invalid resourceType=Bundle")
    if bundle.get("type") not in {"collection", "document", "transaction", "searchset"}:
        errors.append("invalid Bundle.type")
    if not bundle.get("entry"):
        errors.append("Bundle.entry empty")
    seen_types = set()
    for i, e in enumerate(bundle.get("entry", [])):
        r = e.get("resource", {})
        rtype = r.get("resourceType")
        if not rtype:
            errors.append(f"entry[{i}] missing resourceType")
            continue
        if not r.get("id"):
            errors.append(f"entry[{i}] {rtype} missing id")
        seen_types.add(rtype)
        if rtype == "Observation":
            if not r.get("code", {}).get("coding"):
                errors.append(f"entry[{i}] Observation missing code.coding")
            if not r.get("subject"):
                errors.append(f"entry[{i}] Observation missing subject")
    if "Patient" not in seen_types:
        errors.append("Bundle missing Patient resource")
    return {"valid": len(errors) == 0, "errors": errors, "resource_types": sorted(seen_types)}


# ---------------------------------------------------------------------------
# Orchestrator (end-to-end)
# ---------------------------------------------------------------------------
async def run_assessment(
    patient: dict[str, Any],
    biomarkers: dict[str, Any],
    kinematics: dict[str, Any],
    psych_payload: dict[str, Any],
) -> dict[str, Any]:
    chem, phys, psych = await asyncio.gather(
        chemical_agent(biomarkers),
        physical_agent(kinematics),
        psychological_agent(psych_payload),
    )
    negotiation = negotiation_agent(chem, phys, psych)
    alert = dynamic_alert_index(
        consensus_score=negotiation["consensus_score"],
        vas_pain=psych_payload.get("vas_pain", 0),
        bpi_interference=psych_payload.get("bpi_interference", 0),
        dram_distress=psych_payload.get("dram_distress", 0),
        rom_deficit_pct=kinematics.get("rom_deficit_pct", 0),
        snfl_pg_per_ml=biomarkers.get("sNfL_pg_per_ml", 0),
    )
    assessment = {
        "agents": {"chemical": chem, "physical": phys, "psychological": psych},
        "negotiation": negotiation,
        "alert": alert,
    }
    fhir_bundle = build_fhir_bundle(patient, biomarkers, psych_payload, kinematics, assessment)
    fhir_validation = validate_fhir_bundle(fhir_bundle)
    assessment["fhir_bundle"] = fhir_bundle
    assessment["fhir_validation"] = fhir_validation
    return assessment


# ---------------------------------------------------------------------------
# Synthetic payloads (3 cases)
# ---------------------------------------------------------------------------
SYNTHETIC_CASES = {
    "green_low_risk": {
        "patient": {"name": "Asha Iyer", "gender": "female", "birth_date": "1992-04-11"},
        "biomarkers": {
            "sNfL_pg_per_ml": 6.5,
            "gamma_ratio": 1.05,
            "IL6_pg_per_ml": 3.2,
            "TNFa_pg_per_ml": 5.0,
            "IL1b_pg_per_ml": 2.0,
            "substance_p_pg_per_ml": 35.0,
            "BDNF_ng_per_ml": 22.0,
        },
        "kinematics": {
            "rom_deficit_pct": 8,
            "guarding_index": 0.15,
            "hrv_rmssd_ms": 48.0,
            "sleep_efficiency_pct": 88,
            "mean_velocity_mps": 0.75,
        },
        "psych": {
            "vas_pain": 2.0,
            "bpi_interference": 1.5,
            "dram_distress": 18,
            "text_note": "Feeling pretty good today. Light stiffness in the morning, "
                         "managed a 30-minute walk without pain. Mood stable.",
        },
    },
    "yellow_moderate": {
        "patient": {"name": "Rohan Mehta", "gender": "male", "birth_date": "1985-09-22"},
        "biomarkers": {
            "sNfL_pg_per_ml": 18.0,
            "gamma_ratio": 1.55,
            "IL6_pg_per_ml": 8.5,
            "TNFa_pg_per_ml": 12.0,
            "IL1b_pg_per_ml": 5.0,
            "substance_p_pg_per_ml": 85.0,
            "BDNF_ng_per_ml": 14.0,
        },
        "kinematics": {
            "rom_deficit_pct": 24,
            "guarding_index": 0.45,
            "hrv_rmssd_ms": 28.0,
            "sleep_efficiency_pct": 72,
            "mean_velocity_mps": 0.42,
        },
        "psych": {
            "vas_pain": 5.5,
            "bpi_interference": 5.0,
            "dram_distress": 55,
            "text_note": "Pain in lower back is bothering me when I bend. "
                         "I worry that walking too much will make it worse. "
                         "Sleep was patchy, woke twice.",
        },
    },
    "red_high_risk": {
        "patient": {"name": "Maya Singh", "gender": "female", "birth_date": "1978-12-03"},
        "biomarkers": {
            "sNfL_pg_per_ml": 38.0,
            "gamma_ratio": 2.3,
            "IL6_pg_per_ml": 16.0,
            "TNFa_pg_per_ml": 22.0,
            "IL1b_pg_per_ml": 9.0,
            "substance_p_pg_per_ml": 140.0,
            "BDNF_ng_per_ml": 8.0,
        },
        "kinematics": {
            "rom_deficit_pct": 48,
            "guarding_index": 0.78,
            "hrv_rmssd_ms": 14.0,
            "sleep_efficiency_pct": 58,
            "mean_velocity_mps": 0.22,
        },
        "psych": {
            "vas_pain": 8.5,
            "bpi_interference": 8.0,
            "dram_distress": 82,
            "text_note": "Every movement terrifies me. I think the pain will "
                         "destroy my body if I push. I can't focus, brain feels "
                         "foggy. I'm exhausted and hopeless.",
        },
    },
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> int:
    failures = 0
    for case_name, case in SYNTHETIC_CASES.items():
        print(f"\n{'='*70}\nRUNNING CASE: {case_name}\n{'='*70}")
        try:
            result = await run_assessment(
                case["patient"], case["biomarkers"], case["kinematics"], case["psych"]
            )
            agents = result["agents"]
            print(f"  Chemical:      score={agents['chemical']['score']:.2f} conf={agents['chemical']['confidence']:.2f}")
            print(f"    -> {agents['chemical']['narrative']}")
            print(f"  Physical:      score={agents['physical']['score']:.2f} conf={agents['physical']['confidence']:.2f}")
            print(f"    -> {agents['physical']['narrative']}")
            print(f"  Psychological: score={agents['psychological']['score']:.2f} conf={agents['psychological']['confidence']:.2f}")
            print(f"    -> {agents['psychological']['narrative']}")
            neg = result["negotiation"]
            print(f"  Negotiation:   consensus={neg['consensus_score']} σ²={neg['sigma_sq']} flag={neg['validation_flag']} outlier={neg['outlier_agent']}")
            alert = result["alert"]
            print(f"  I_alert:       {alert['i_alert']} → TIER {alert['tier']}")
            print(f"    actions: {alert['recommended_actions']}")
            fv = result["fhir_validation"]
            print(f"  FHIR:          valid={fv['valid']} resources={fv['resource_types']}")
            if not fv["valid"]:
                print(f"    ERRORS: {fv['errors']}")
                failures += 1

            # Sanity checks per case
            if case_name == "green_low_risk" and alert["tier"] not in {"GREEN", "YELLOW"}:
                print(f"  [SANITY-FAIL] expected GREEN/YELLOW, got {alert['tier']}")
                failures += 1
            if case_name == "red_high_risk" and alert["tier"] != "RED":
                print(f"  [SANITY-FAIL] expected RED, got {alert['tier']}")
                failures += 1
        except Exception as e:  # noqa: BLE001
            print(f"  CASE FAILED: {e!r}")
            failures += 1

    print(f"\n{'='*70}\nPOC SUMMARY: failures={failures} / cases={len(SYNTHETIC_CASES)}\n{'='*70}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

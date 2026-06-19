"""FHIR R4 mapping + validation for HelixCortex assessments."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

LOINC = {
    "sNfL": ("82293-6", "Neurofilament light chain [Mass/volume] in Serum or Plasma"),
    "glutamate": ("14749-6", "Glutamate [Mass/volume] in Serum"),
    "gaba": ("LP38458-1", "Gamma-aminobutyric acid"),
    "IL6": ("26881-3", "Interleukin 6 [Mass/volume] in Serum or Plasma"),
    "TNFa": ("57835-4", "Tumor necrosis factor alpha [Mass/volume]"),
    "IL1b": ("LP14916-9", "Interleukin 1 beta"),
    "VAS_pain": ("72514-3", "Pain severity - 0-10 verbal numeric rating"),
    "BPI": ("75441-6", "Brief pain inventory short form"),
    "HRV_rmssd": ("80404-9", "Heart rate variability - RMSSD"),
    "ROM": ("71907-0", "Range of motion of joint"),
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

    entries.append({
        "resource": {
            "resourceType": "Patient",
            "id": patient_id,
            "name": [{"text": patient.get("name", "Unknown Patient")}],
            "gender": patient.get("gender", "unknown"),
            "birthDate": patient.get("birth_date", "1980-01-01"),
        }
    })

    def obs(loinc_key: str, value: float, unit: str) -> dict[str, Any]:
        code, display = LOINC[loinc_key]
        return {
            "resource": {
                "resourceType": "Observation",
                "id": str(uuid.uuid4()),
                "status": "final",
                "code": {"coding": [{"system": "http://loinc.org", "code": code, "display": display}]},
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": now,
                "valueQuantity": {"value": value, "unit": unit},
            }
        }

    mapping = [
        ("sNfL_pg_per_ml", "sNfL", "pg/mL", biomarkers),
        ("IL6_pg_per_ml", "IL6", "pg/mL", biomarkers),
        ("TNFa_pg_per_ml", "TNFa", "pg/mL", biomarkers),
        ("IL1b_pg_per_ml", "IL1b", "pg/mL", biomarkers),
        ("vas_pain", "VAS_pain", "{score}", psych_payload),
        ("bpi_interference", "BPI", "{score}", psych_payload),
        ("hrv_rmssd_ms", "HRV_rmssd", "ms", kinematics),
        ("rom_deficit_pct", "ROM", "%", kinematics),
    ]
    for src_key, loinc_key, unit, src in mapping:
        if src and src_key in src and src[src_key] is not None:
            entries.append(obs(loinc_key, float(src[src_key]), unit))

    snomed_code, snomed_display = SNOMED["nociplastic_pain"]
    entries.append({
        "resource": {
            "resourceType": "DiagnosticReport",
            "id": str(uuid.uuid4()),
            "status": "final",
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": snomed_code, "display": snomed_display}]},
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": now,
            "conclusion": (
                f"HelixCortex multi-agent assessment \u2014 Tier {assessment['alert']['tier']}, "
                f"I_alert={assessment['alert']['i_alert']}, "
                f"\u03c3\u00b2={assessment['negotiation']['sigma_sq']}, "
                f"validation_flag={assessment['negotiation']['validation_flag']}."
            ),
        }
    })

    return {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "collection",
        "timestamp": now,
        "entry": entries,
    }


def validate_fhir_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(bundle, dict):
        return {"valid": False, "errors": ["bundle is not a JSON object"], "resource_types": []}
    if bundle.get("resourceType") != "Bundle":
        errors.append("missing/invalid resourceType=Bundle")
    if bundle.get("type") not in {"collection", "document", "transaction", "searchset"}:
        errors.append("invalid Bundle.type")
    if not bundle.get("entry"):
        errors.append("Bundle.entry empty")
    seen: set[str] = set()
    for i, e in enumerate(bundle.get("entry", []) or []):
        r = (e or {}).get("resource", {}) or {}
        rtype = r.get("resourceType")
        if not rtype:
            errors.append(f"entry[{i}] missing resourceType")
            continue
        if not r.get("id"):
            errors.append(f"entry[{i}] {rtype} missing id")
        seen.add(rtype)
        if rtype == "Observation":
            if not r.get("code", {}).get("coding"):
                errors.append(f"entry[{i}] Observation missing code.coding")
            if not r.get("subject"):
                errors.append(f"entry[{i}] Observation missing subject")
    if "Patient" not in seen:
        errors.append("Bundle missing Patient resource")
    return {"valid": not errors, "errors": errors, "resource_types": sorted(seen)}

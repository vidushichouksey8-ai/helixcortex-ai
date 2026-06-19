"""HelixCortex Labs FastAPI backend.

Multi-agent decision support: Chemical/Physical/Psychological agents \u2192
Negotiation (\u03c3\u00b2 consensus) \u2192 Dynamic Alerting Index \u2192 FHIR R4.
"""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from agents import chemical_agent, physical_agent, psychological_agent  # noqa: E402
from fhir_service import build_fhir_bundle, validate_fhir_bundle  # noqa: E402
from orchestrator import dynamic_alert_index, negotiation_agent  # noqa: E402
from synthetic import generate_synthetic_case  # noqa: E402
import asyncio  # noqa: E402

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="HelixCortex Labs API")
api = APIRouter(prefix="/api")

logger = logging.getLogger("helixcortex")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    gender: str = "unknown"
    birth_date: str = "1980-01-01"
    mrn: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_tier: Optional[str] = None
    last_i_alert: Optional[float] = None
    last_assessment_at: Optional[str] = None


class PatientCreate(BaseModel):
    name: str
    gender: str = "unknown"
    birth_date: str = "1980-01-01"
    mrn: Optional[str] = None
    notes: Optional[str] = None


class AssessmentRequest(BaseModel):
    patient_id: str
    biomarkers: dict[str, Any] = Field(default_factory=dict)
    kinematics: dict[str, Any] = Field(default_factory=dict)
    psych: dict[str, Any] = Field(default_factory=dict)


class MemoDecision(BaseModel):
    decision: str  # 'approve' | 'contest' | 'override'
    rationale: str
    clinician: str = "demo-clinician"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _audit(actor: str, action: str, entity_type: str, entity_id: str, details: dict[str, Any]) -> None:
    event = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details,
    }
    await db.audit_events.insert_one(event)


def _strip_id(d: dict[str, Any]) -> dict[str, Any]:
    d.pop("_id", None)
    return d


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@api.get("/")
async def root():
    return {"service": "HelixCortex Labs", "status": "online", "version": "1.0.0"}


@api.get("/health")
async def health():
    return {"ok": True, "llm_key_loaded": bool(os.environ.get("EMERGENT_LLM_KEY"))}


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------
@api.post("/patients", response_model=Patient)
async def create_patient(payload: PatientCreate):
    p = Patient(**payload.model_dump())
    doc = p.model_dump()
    await db.patients.insert_one(doc.copy())
    await _audit("clinician", "patient.create", "patient", p.id, {"name": p.name})
    return p


@api.get("/patients")
async def list_patients():
    docs = await db.patients.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return docs


@api.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    doc = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "patient not found")
    return doc


@api.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str):
    res = await db.patients.delete_one({"id": patient_id})
    await db.assessments.delete_many({"patient_id": patient_id})
    await db.context_memos.delete_many({"patient_id": patient_id})
    await _audit("clinician", "patient.delete", "patient", patient_id, {"deleted": res.deleted_count})
    return {"deleted": res.deleted_count}


# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------
@api.post("/synthetic/generate")
async def synthetic_generate(severity: Optional[str] = None, persist: bool = False):
    case = generate_synthetic_case(severity)
    if persist:
        await db.patients.insert_one(case["patient"].copy())
        await _audit("system", "patient.synthetic_create", "patient", case["patient"]["id"], {"severity": case["severity_hint"]})
    return case


# ---------------------------------------------------------------------------
# Run assessment (Chemical + Physical + Psychological + Negotiation + I_alert + FHIR)
# ---------------------------------------------------------------------------
@api.post("/assessment/run")
async def assessment_run(req: AssessmentRequest):
    patient = await db.patients.find_one({"id": req.patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(404, "patient not found")

    chem, phys, psych = await asyncio.gather(
        chemical_agent(req.biomarkers),
        physical_agent(req.kinematics),
        psychological_agent(req.psych),
    )
    negotiation = negotiation_agent(chem, phys, psych)
    alert = dynamic_alert_index(
        consensus_score=negotiation["consensus_score"],
        vas_pain=req.psych.get("vas_pain", 0),
        bpi_interference=req.psych.get("bpi_interference", 0),
        dram_distress=req.psych.get("dram_distress", 0),
        rom_deficit_pct=req.kinematics.get("rom_deficit_pct", 0),
        snfl_pg_per_ml=req.biomarkers.get("sNfL_pg_per_ml", 0),
    )
    assessment = {
        "id": str(uuid.uuid4()),
        "patient_id": req.patient_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {"biomarkers": req.biomarkers, "kinematics": req.kinematics, "psych": req.psych},
        "agents": {"chemical": chem, "physical": phys, "psychological": psych},
        "negotiation": negotiation,
        "alert": alert,
    }
    fhir_bundle = build_fhir_bundle(patient, req.biomarkers, req.psych, req.kinematics, assessment)
    fhir_val = validate_fhir_bundle(fhir_bundle)
    assessment["fhir_bundle"] = fhir_bundle
    assessment["fhir_validation"] = fhir_val

    await db.assessments.insert_one(assessment.copy())
    await db.patients.update_one(
        {"id": req.patient_id},
        {"$set": {
            "last_tier": alert["tier"],
            "last_i_alert": alert["i_alert"],
            "last_assessment_at": assessment["created_at"],
        }},
    )
    await _audit("clinician", "assessment.run", "assessment", assessment["id"], {
        "patient_id": req.patient_id, "tier": alert["tier"], "i_alert": alert["i_alert"],
        "sigma_sq": negotiation["sigma_sq"], "validation_flag": negotiation["validation_flag"],
    })

    if negotiation["context_memo"]:
        memo = {
            **negotiation["context_memo"],
            "patient_id": req.patient_id,
            "assessment_id": assessment["id"],
            "tier": alert["tier"],
            "i_alert": alert["i_alert"],
            "sigma_sq": negotiation["sigma_sq"],
            "decision": None,
            "decision_rationale": None,
            "decided_by": None,
            "decided_at": None,
        }
        await db.context_memos.insert_one(memo.copy())
        await _audit("system", "memo.create", "context_memo", memo["memo_id"], {"patient_id": req.patient_id, "reason": memo["reason"]})

    return _strip_id(assessment)


@api.get("/assessments/{patient_id}")
async def list_assessments(patient_id: str, limit: int = 25):
    docs = await db.assessments.find({"patient_id": patient_id}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return docs


@api.get("/assessments/by-id/{assessment_id}")
async def get_assessment(assessment_id: str):
    doc = await db.assessments.find_one({"id": assessment_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "assessment not found")
    return doc


# ---------------------------------------------------------------------------
# Context Memos (HITL queue)
# ---------------------------------------------------------------------------
@api.get("/memos")
async def list_memos(status: Optional[str] = None):
    q: dict[str, Any] = {}
    if status:
        q["status"] = status
    docs = await db.context_memos.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)
    return docs


@api.get("/memos/{memo_id}")
async def get_memo(memo_id: str):
    doc = await db.context_memos.find_one({"memo_id": memo_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "memo not found")
    return doc


@api.post("/memos/{memo_id}/decision")
async def memo_decision(memo_id: str, payload: MemoDecision):
    if payload.decision not in {"approve", "contest", "override"}:
        raise HTTPException(400, "decision must be approve|contest|override")
    if len(payload.rationale.strip()) < 20:
        raise HTTPException(400, "rationale must be at least 20 characters (Contestable AI audit policy)")
    new_status = {
        "approve": "approved",
        "contest": "contested",
        "override": "overridden",
    }[payload.decision]
    now = datetime.now(timezone.utc).isoformat()
    res = await db.context_memos.update_one(
        {"memo_id": memo_id},
        {"$set": {
            "status": new_status,
            "decision": payload.decision,
            "decision_rationale": payload.rationale,
            "decided_by": payload.clinician,
            "decided_at": now,
        }},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "memo not found")
    await _audit(payload.clinician, f"memo.{payload.decision}", "context_memo", memo_id, {"rationale": payload.rationale})
    return {"ok": True, "status": new_status}


# ---------------------------------------------------------------------------
# FHIR
# ---------------------------------------------------------------------------
@api.post("/fhir/validate")
async def fhir_validate(request: Request):
    body = await request.json()
    val = validate_fhir_bundle(body)
    return val


@api.get("/fhir/export/{assessment_id}")
async def fhir_export(assessment_id: str):
    doc = await db.assessments.find_one({"id": assessment_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "assessment not found")
    await _audit("clinician", "fhir.export", "assessment", assessment_id, {})
    return doc.get("fhir_bundle", {})


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
@api.get("/audit")
async def list_audit(limit: int = 200):
    docs = await db.audit_events.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return docs


# ---------------------------------------------------------------------------
# Education content (static)
# ---------------------------------------------------------------------------
@api.get("/education/taxonomy")
async def education_taxonomy():
    return {
        "taxonomy": [
            {
                "category": "Nociceptive",
                "etiology": "Active tissue damage or localized inflammatory cascade.",
                "diagnostic_evidence": "Localized nociceptor activation; standard inflammatory markers.",
                "examples": ["Rheumatoid arthritis", "Osteoarthritis", "Acute trauma"],
            },
            {
                "category": "Neuropathic",
                "etiology": "Lesion or disease of the somatosensory nervous system.",
                "diagnostic_evidence": "Demonstrable nerve damage via EMG, NCS, or neuroimaging.",
                "examples": ["Diabetic neuropathy", "Sciatica", "Post-herpetic neuralgia"],
            },
            {
                "category": "Nociplastic",
                "etiology": "CNS dysfunction, amplified sensory processing, neuroimmune dysregulation.",
                "diagnostic_evidence": "Objective biometrics + sensitization metrics (HelixCortex).",
                "examples": ["Fibromyalgia", "IBS", "Chronic primary headaches"],
            },
        ],
        "gamma_ratio": {
            "formula": "\u03b3 = [Glutamate] / [GABA]",
            "explanation": "Excitatory/inhibitory balance. Elevated \u03b3 indicates a system stuck in the ON position.",
        },
        "context": {
            "recognition": "Formally recognized in 2021 by The Lancet and the IASP as a third primary pain mechanism.",
            "sensitization_chain": [
                "Glial-neuronal interaction (TLR4 activation, MAPK signaling)",
                "Cytokine storm: IL-1\u03b2, IL-6, TNF-\u03b1",
                "Supraspinal hyper-responsiveness (mPFC, ACC, thalamus)",
            ],
            "hitl": "HelixCortex acts as decision-SUPPORT. Final authority rests with the clinician.",
        },
    }


# ---------------------------------------------------------------------------
# Mount + middleware
# ---------------------------------------------------------------------------
app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db():
    client.close()

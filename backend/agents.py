"""HelixCortex specialist AI agents (Chemical, Physical, Psychological).

Each agent calls Emergent Universal LLM and returns a STRICT JSON output:
  { score: float[0,1], confidence: float[0,1], narrative: str, key_findings: list[str] }
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from typing import Any

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

from emergentintegrations.llm.chat import LlmChat, UserMessage  # noqa: E402

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-sonnet-4-6"

CLINICAL_REFS = {
    "sNfL_pg_per_ml": {"healthy_max": 10.0, "elevated": 20.0, "high": 35.0},
    "gamma_ratio": {"healthy": 1.0, "elevated": 1.5, "high": 2.0},
    "IL6_pg_per_ml": {"normal_max": 5.0, "elevated": 10.0},
    "TNFa_pg_per_ml": {"normal_max": 8.0, "elevated": 15.0},
    "IL1b_pg_per_ml": {"normal_max": 3.0, "elevated": 6.0},
    "substance_p_pg_per_ml": {"normal_max": 50.0, "elevated": 100.0},
    "BDNF_ng_per_ml": {"normal": 20.0, "elevated_low": 10.0},
    "HRV_rmssd_ms": {"healthy_min": 35.0, "low": 20.0},
    "ROM_deficit_pct": {"mild": 10, "moderate": 25, "severe": 40},
    "VAS_pain": {"min": 0, "max": 10, "high": 7},
    "DRAM_distress": {"min": 0, "max": 100, "high": 60},
}

AGENT_SCHEMA = {
    "score": "float in [0,1]",
    "confidence": "float in [0,1]",
    "narrative": "1-3 sentence clinical narrative",
    "key_findings": "list[str] of 2-5 concise findings",
}

SYSTEM_BASE = (
    "You are a specialist clinical AI agent in the HelixCortex Labs decoupled "
    "multi-agent diagnostic platform for nociplastic pain. You ONLY output a JSON "
    "object with keys: score (0-1), confidence (0-1), narrative (string), "
    "key_findings (array of strings). Never include code fences or commentary."
)


def _extract_json(text: str) -> dict[str, Any]:
    if not text:
        raise ValueError("empty LLM response")
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    s = cleaned.find("{")
    e = cleaned.rfind("}")
    if s == -1 or e == -1 or e <= s:
        raise ValueError(f"no JSON in: {text[:200]}")
    return json.loads(cleaned[s : e + 1])


def _coerce(raw: dict[str, Any]) -> dict[str, Any]:
    score = float(raw.get("score", 0.0))
    conf = float(raw.get("confidence", 0.5))
    narrative = str(raw.get("narrative", "")).strip() or "No narrative provided."
    findings = raw.get("key_findings", []) or []
    if isinstance(findings, str):
        findings = [findings]
    findings = [str(f) for f in findings][:6]
    return {
        "score": max(0.0, min(1.0, score)),
        "confidence": max(0.0, min(1.0, conf)),
        "narrative": narrative,
        "key_findings": findings,
    }


async def _call(agent_name: str, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not EMERGENT_LLM_KEY:
        return _fallback(agent_name, "missing_emergent_llm_key")

    user_text = (
        f"Analyze this patient payload as the {agent_name}. "
        f"Reference ranges: {json.dumps(CLINICAL_REFS)}. "
        f"PAYLOAD:\n{json.dumps(payload, indent=2)}\n\n"
        f"Respond ONLY with JSON matching: {json.dumps(AGENT_SCHEMA)}"
    )
    last_err: Exception | None = None
    for _ in range(2):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"hc-{agent_name}-{uuid.uuid4()}",
                system_message=system_prompt,
            ).with_model(LLM_PROVIDER, LLM_MODEL)
            resp = await chat.send_message(UserMessage(text=user_text))
            text = resp if isinstance(resp, str) else getattr(resp, "content", str(resp))
            return _coerce(_extract_json(text))
        except Exception as e:  # noqa: BLE001
            last_err = e
            await asyncio.sleep(0.4)
    return _fallback(agent_name, str(last_err))


def _fallback(agent_name: str, reason: str) -> dict[str, Any]:
    return {
        "score": 0.5,
        "confidence": 0.2,
        "narrative": f"{agent_name} fallback engaged ({reason}). Manual clinician review required.",
        "key_findings": ["llm_unavailable", "manual_review_required"],
    }


async def chemical_agent(biomarkers: dict[str, Any]) -> dict[str, Any]:
    sys_msg = (
        SYSTEM_BASE
        + " You are the Chemical Agent. Evaluate systemic neuroinflammation and "
        "neurotoxicity from sNfL, gamma_ratio (Glu/GABA), cytokines (IL-1\u03b2/IL-6/TNF-\u03b1), "
        "Substance P, BDNF. Higher dysregulation \u2192 higher score."
    )
    return await _call("Chemical Agent", sys_msg, biomarkers)


async def physical_agent(kinematics: dict[str, Any]) -> dict[str, Any]:
    sys_msg = (
        SYSTEM_BASE
        + " You are the Physical Agent. Evaluate kinetic sensitization from VR "
        "kinematics (joint coords, velocity, ROM deficits, guarding), HRV rmssd, "
        "sleep efficiency. Higher dysfunction \u2192 higher score."
    )
    return await _call("Physical Agent", sys_msg, kinematics)


async def psychological_agent(psych_payload: dict[str, Any]) -> dict[str, Any]:
    sys_msg = (
        SYSTEM_BASE
        + " You are the Psychological Agent. Use NLP-style reasoning to identify "
        "pain catastrophizing, kinesiophobia, anxiety, brain fog from patient text "
        "and EMA scales (VAS, BPI interference, DRAM distress). Higher distress \u2192 higher score."
    )
    return await _call("Psychological Agent", sys_msg, psych_payload)

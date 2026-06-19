# HelixCortex Labs — plan.md

## 1) Objectives
- Prove the **core workflow** works end-to-end: multi-agent scoring (Chemical/Physical/Psychological) → Negotiation (σ²) → HITL Context Memo → Dynamic Alerting Index (GREEN/YELLOW/RED) → FHIR R4 import/export.
- Ship an MVP app (FastAPI + React) built **around the proven core**, with synthetic data + manual entry + FHIR upload, and Three.js kinematics simulation.
- Add Emergent Google OAuth + role-based UX (Clinician/Patient) after V1 stability.
- Deliver a backend-focused pytest suite covering agent logic, consensus math, tiering, FHIR validation, and API endpoints.

---

## 2) Implementation Steps (Phased)

### Phase 1 — Core Workflow POC (Isolation; must pass before app)
**Goal:** minimal Python POC validating external LLM integration + core orchestration logic.

1. Web research (targeted): best practices for (a) LLM agent output schemas + retry/validation, (b) FHIR R4 Observation/DiagnosticReport mapping for pain/biomarkers.
2. Create `poc_core_flow.py`:
   - Inputs: biomarker dict, kinematics dict, EMA+text dict (plus optional VAS/function).
   - Emergent Universal LLM Key calls for 3 specialist agents; enforce JSON schema output: `{score_0_1, confidence_0_1, narrative, key_findings[]}`.
   - Negotiation Agent: standardize outputs, compute **σ² = variance(z_scores)**, compare to `θ_safe`, emit `validation_flag` + Context Memo.
   - Dynamic Alerting Index `I_alert`: compute composite + tier classification (GREEN/YELLOW/RED with 1.4× rule).
   - FHIR: generate Patient + Observations + DiagnosticReport; validate structure (basic JSON schema checks + required fields).
3. Add `poc_synthetic_payloads.py` to generate realistic demo payloads (sNfL ranges, cytokines, γ ratio, HRV/sleep, joint vectors, EMA scales).
4. Add `tests/test_poc_core.py` (pytest) asserting:
   - LLM outputs parse/validate; deterministic fallbacks when malformed.
   - σ² math correct; flagging triggers at threshold.
   - I_alert tier boundaries correct.
   - FHIR payload contains required resources + codes.
5. Iterate until POC is stable and repeatable.

**Phase 1 user stories**
- As a developer, I can run one script to execute the entire agent→negotiation→alert→FHIR pipeline.
- As a developer, I get a clear error when an agent returns invalid JSON and see the auto-retry behavior.
- As a developer, I can generate synthetic patient cases that produce GREEN/YELLOW/RED tiers.
- As a developer, I can see when σ² exceeds θ_safe and a Context Memo is produced.
- As a developer, I can export a valid FHIR R4 bundle for a completed assessment.

---

### Phase 2 — V1 App Development (MVP around proven core; no OAuth yet)
**Goal:** working product flow first; keep auth stubbed/off to maximize testability.

1. Backend (FastAPI)
   - Core modules: `agents/chemical.py`, `agents/physical.py`, `agents/psychological.py`, `orchestrator/negotiation.py`, `orchestrator/alert_index.py`, `fhir/mapping.py`, `fhir/validation.py`.
   - API endpoints:
     - `POST /api/assessment/run` (runs all agents + σ² + I_alert + memo)
     - `POST /api/synthetic/generate`
     - `POST /api/fhir/validate` (upload JSON)
     - `POST /api/fhir/export` (returns bundle)
     - `GET /api/audit-log` (append-only events)
     - Minimal patient CRUD for demo: `POST/GET /api/patients`
   - Persistence (MongoDB): patients, assessments, context_memos, audit_events.
2. Frontend (React + shadcn/ui)
   - Screens:
     - Home: create/select patient, run assessment
     - Manual entry forms: biomarkers, EMA, text note, kinematics toggles
     - Synthetic generator: one-click populate forms
     - Results: per-agent cards (score/confidence/narrative), σ² + validation flag, I_alert tier banner + recommended actions
     - Context Memo viewer (read-only in V1)
     - FHIR import/export UI
     - Education module page (taxonomy + γ ratio explanation)
   - Three.js / React Three Fiber:
     - Simulated skeleton/joint markers + velocity vectors
     - ROM overlay + “guarding” highlight (simple heuristic)
3. Wire audit logging: every assessment run + memo creation + export/import logged.
4. One round of E2E testing (testing agent): manual entry → run → results → FHIR export → upload validate.

**Phase 2 user stories**
- As a clinician, I can enter biomarkers/EMA/kinematics and run a full assessment in one click.
- As a clinician, I can see separate agent scores with confidence and narratives.
- As a clinician, I can view the σ² disagreement metric and whether human validation is required.
- As a clinician, I can view a 3D kinematics simulation with ROM overlays.
- As a clinician, I can export the assessment as a FHIR R4 payload and validate an uploaded payload.

---

### Phase 3 — Add Auth + Roles + HITL Actions (Emergent Google OAuth)
**Goal:** production-like access control once V1 is stable.

1. Integrate Emergent Google OAuth (backend + frontend): session handling, callback, token verification.
2. Roles + permissions:
   - Clinician: patient list, all assessments, memo queue, override actions.
   - Patient: only own profile, EMA submission, view simplified results.
3. HITL governance:
   - Context Memo queue: `GET/POST /api/context-memos` (approve/contest/override)
   - “Go/No-Go” verification: require clinician confirmation when RED or when σ²>θ_safe.
   - Lock write-access behavior on RED (server-enforced).
4. E2E test pass: clinician vs patient access boundaries.

**Phase 3 user stories**
- As a clinician, I can sign in with Google and see my patient dashboard.
- As a patient, I can sign in with Google and submit EMA scores on mobile.
- As a clinician, I can review a Context Memo and approve/override the recommendation.
- As a clinician, I can see that RED tier locks further training updates until triage is completed.
- As an admin/developer, I can verify audit logs contain who approved/overrode and when.

---

### Phase 4 — Comprehensive Testing, Hardening, and Release Readiness
1. Expand pytest suite:
   - Agent unit tests (schema, scoring ranges, confidence bounds)
   - Negotiation σ² + threshold tests
   - Alert index tiering tests incl. 1.4× rule
   - FHIR mapping tests incl. SNOMED/LOINC code presence
   - API endpoint tests (happy path + malformed payloads + auth required routes)
2. Reliability:
   - LLM retry/backoff, timeouts, structured output validation
   - Deterministic fallback narratives when LLM unavailable
3. Security + compliance basics:
   - PII handling, minimal logging of sensitive fields, secure storage of tokens
4. Final E2E run (testing agent) on full app.

**Phase 4 user stories**
- As a developer, I can run `pytest` and get high confidence core logic won’t regress.
- As a clinician, I can trust the system won’t silently proceed when agents disagree beyond θ_safe.
- As a clinician, I can upload malformed FHIR and get actionable validation errors.
- As a patient, I see only my data and nothing else.
- As a product owner, I can demo GREEN/YELLOW/RED flows reliably using synthetic cases.

---

## 3) Next Actions (Immediate)
1. Implement Phase 1 POC scripts + minimal pytest.
2. Confirm core formulas/weights for `I_alert` (defaults if not provided).
3. Define θ_safe initial value and z-score standardization method (per-run vs population baseline).
4. Draft LOINC/SNOMED code list for the specific biomarkers/assessments included in MVP.

---

## 4) Success Criteria
- Phase 1: POC script runs successfully 10 times with synthetic payloads; produces valid agent JSON, σ², Context Memo when appropriate, I_alert tier, and a valid FHIR bundle.
- Phase 2: V1 app supports manual entry + synthetic generation + FHIR upload/export + 3D kinematics view; end-to-end demo works without manual DB edits.
- Phase 3: Google OAuth works end-to-end; clinician/patient role restrictions enforced; HITL overrides recorded in audit log.
- Phase 4: pytest suite covers core logic + endpoints; no critical issues found in final E2E test; regression-safe core workflow.
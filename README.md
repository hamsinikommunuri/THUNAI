# THUNAI (துணை) — Component 1: Deterministic Safety Engine

THUNAI is an AI-powered agricultural advisory system with a strict, non-negotiable architectural invariant:

> **No agricultural action becomes a recommendation merely because an AI model generated it. It becomes a recommendation only after evidence, context, and deterministic safety gates permit it.**

The LLM is strictly decoupled from dosage authorization. The LLM may understand farmer intent, translate into colloquial Tamil, and format explanations, but **it cannot authorize a chemical recommendation or dosage**. That decision belongs exclusively to this deterministic safety engine.

---

## 1. Phase 1 Scope: 4 Controlled Crops

Phase 1 is a controlled safety-validation environment designed to mathematically prove zero cross-crop dose leakage, robust context isolation, and regulatory enforcement across:

1. **Paddy / நெல்** (*Oryza sativa*)
2. **Tomato / தக்காளி** (*Solanum lycopersicum*)
3. **Banana / வாழை** (*Musa acuminata*)
4. **Chilli / மிளகாய்** (*Capsicum annuum*)

---

## 2. Architecture & Deliverables

```
thunai/
├── core/
│   ├── enums.py            # DecisionType, ReasonCategory, ReasonCode, CropId, SourceTier, EvidenceStatus
│   ├── models.py           # FarmerContext, EvidenceRecord, DoseEvidence, SafetyDecision, ActionDecision
│   └── normalizer.py       # Entity & chemical normalizer (Active Ingredient + Formulation + Concentration)
└── safety/
    ├── context_isolation.py   # Hard agricultural filters, prompt injection check, cross-crop isolation
    ├── chemical_safety.py     # CIBRC statutory bans, restrictions, label claims, WHO toxicity policies
    ├── evidence_validation.py # Source verification (TNAU/ICAR), completeness, explicit positive dose
    ├── dose_lock.py           # The Dose Lock state machine (LOCKED by default)
    └── escalation.py          # Action decisions, human agronomist escalation, bilingual explanations (EN/TA)
```

---

## 3. The Dose Lock Principle

Dose Lock is **LOCKED by default**. It unlocks only when all required agricultural gates evaluate to TRUE:

$$\text{DoseAllowed} = \text{TrustedSource} \land \text{CropMatch} \land \text{ProblemMatch} \land \text{ProductMatch} \land \text{ExplicitDoseExists} \land \text{ChemicalAllowed}$$

If any required condition is false or unknown:
$$\text{DoseAllowed} = \text{FALSE}$$

**Zero Invented Doses**: When locked, THUNAI never generates a speculative or fallback dose. It explains the exact reason code and escalates or requests clarification.

---

## 4. Reason Taxonomy (Never Collapsed into Generic Flags)

THUNAI categorizes every safety decision into five distinct operational domains:

1. **LEGAL_REGULATORY**: Statutory prohibitions under the Insecticides Act 1968 / CIBRC / Supreme Court notifications (`BANNED_CHEMICAL`, `RESTRICTED_CHEMICAL`, `UNREGISTERED_LABEL_CLAIM`).
2. **EVIDENCE_MISMATCH**: Agricultural context mismatch (`CROP_MISMATCH`, `PROBLEM_MISMATCH`, `CHEMICAL_MISMATCH`, `CROSS_CROP_LEAKAGE`).
3. **PRODUCT_SAFETY_POLICY**: THUNAI safety rules (`HIGH_TOXICITY_RESTRICTION`, `PRE_HARVEST_INTERVAL_VIOLATION`, `HAZARDOUS_TANK_MIX`).
4. **WEATHER_GATE**: Environmental spraying constraints (`RAIN_GATED`, `WIND_GATED`, `TEMPERATURE_GATED`).
5. **UNCERTAINTY**: Incomplete or unverified input data (`AMBIGUOUS_CROP`, `AMBIGUOUS_PROBLEM`, `UNKNOWN_CROP`, `MISSING_EVIDENCE`, `MISSING_EXPLICIT_DOSE`, `INVALID_DOSE_VALUE`, `INCOMPLETE_METADATA`, `UNVERIFIED_SOURCE`, `UNVERIFIED_STATUS`, `CONFLICTING_EVIDENCE`, `PROMPT_INJECTION_DETECTED`).

---

## 5. Automated Regression Test Suite (83 Gold Cases)

The reconstructed 83-case safety suite (`tests/test_gold_safety_suite.py`) verifies real agricultural failure modes:

| Category | Cases | Target Failure Mode Tested |
| :--- | :---: | :--- |
| **1. Valid Verified Recommendation** | GOLD-001 – GOLD-008 | Verified TNAU/CIBRC approvals across all 4 crops |
| **2. Missing / Invalid Dose** | GOLD-009 – GOLD-014 | `dose=None`, `dose=0.0`, negative doses, missing units |
| **3. Wrong Crop** | GOLD-015 – GOLD-020 | Direct crop context vs evidence collisions |
| **4. Wrong Pest / Disease** | GOLD-021 – GOLD-026 | Sucking pest vs fungal disease mismatches |
| **5. Cross-Crop Retrieval Collision** | GOLD-027 – GOLD-034 | Multi-candidate cross-crop leakage prevention |
| **6. Unsupported Chemical** | GOLD-035 – GOLD-039 | Off-label unapproved chemical usage |
| **7. Prohibited / Restricted Chemical** | GOLD-040 – GOLD-047 | Monocrotophos, Endosulfan, Furadan, Paraquat, etc. |
| **8. Ambiguous Farmer Query** | GOLD-048 – GOLD-052 | Missing crop, vague symptoms, unsupported crops |
| **9. Tamil Queries** | GOLD-053 – GOLD-058 | Native Tamil queries correctly isolated & verified |
| **10. Tanglish Queries** | GOLD-059 – GOLD-064 | Romanized Tamil colloquial queries |
| **11. Spelling Variations** | GOLD-065 – GOLD-069 | Crop and pest typo tolerance |
| **12. Prompt Injection Resistance** | GOLD-070 – GOLD-074 | "ignore safety" adversarial bypass attempts |
| **13. Missing Evidence** | GOLD-075 – GOLD-078 | Empty candidate lists / no records in corpus |
| **14. Conflicting Evidence** | GOLD-079 – GOLD-080 | Contradictory dosage entries in database |
| **15. Incomplete Metadata & Sources** | GOLD-081 – GOLD-083 | Missing active ingredient, formulation, unverified blogs |

### Running the Tests

```bash
# Run all 150 automated tests (unit tests + 83 gold regression suite)
python -m pytest -v

# Run only the 83 gold safety regression suite
python -m pytest tests/test_gold_safety_suite.py -v
```

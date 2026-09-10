# ProcRun — final product foundation

Status: **CURRENT — EVIDENCE-BOUNDED OWN-CODE FOUNDATION**
Date: 2026-09-10

`docs/BUILD_GATES.md` is the authoritative release decision and `docs/EVIDENCE_BOUNDED_PRODUCTION_SEMANTICS.md` is the authoritative intelligence-semantics contract. Earlier A21/A21a material is research provenance only and must never be used to imply that an uncompleted human-gold benchmark passed.

## 1. Product definition

ProcRun is a supplier-side infrastructure procurement product. The production runway mechanism is:

`approved funded project -> exact source-evidenced purchasable components -> approved procurement evidence -> conservative matching -> component state -> project state -> customer-safe runway`

ProcRun is not a general tender portal, CRM, bid writer, buyer-intelligence suite, AI GO/NO-GO scorer or person/contact-intelligence product.

## 2. Trust contract and OPEN scope

Marketing may say:

> **No invented demand. Source evidence for every positive procurement match.**

`100% source-verified` is allowed only for an evidence object that actually satisfies its exact provenance contract.

For production, `OPEN` means exactly:

> **No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED as of DATE.**

This is a rule-bounded observation, not a universal absence claim. Every customer surface that renders or exports OPEN must state that it does not establish absence outside TED or under different wording/classification.

## 3. State ontology

### Component states

- **CLOSED** — a pre-cutoff TED record satisfies the frozen structural match requirements and carries exact accepted source evidence for the component.
- **OPEN** — complete TED coverage exists through the cutoff, the component boundary is resolved, and no accepted or unresolved plausible candidate remains under the frozen exact-evidence rules.
- **UNRESOLVED** — ambiguity, unmatched source wording, plausible unresolved candidates, incomplete coverage or insufficient evidence prevents a safe OPEN/CLOSED result.

### Project states

Project states are `OPEN`, `PARTIAL`, `CLOSED`, `UNRESOLVED`. Any unresolved component makes the project UNRESOLVED. All CLOSED => CLOSED; all OPEN => OPEN; a fully resolved OPEN/CLOSED mixture => PARTIAL. A project with no safely extracted component is UNRESOLVED and remains represented with its verbatim approved source wording.

False or over-broad OPEN is the highest-cost classification error.

## 4. Source strategy

### 4.1 TED

TED Search API is approved only through the frozen server-side field projection used by ProcRun. Complete bounded pagination and schema validation are mandatory. TED provides procurement evidence and the rule-bounded OPEN observation universe; it is not represented as complete national procurement coverage.

### 4.2 OpenCoesione

OpenCoesione is approved only for the exact bounded 2021–2027 EU-cohesion operation-list publication family already qualified by the source contract. `OperationLocalIdentifier` is the logical project identity. CUP is retained only as a procurement-reference alias and may never collapse distinct operations.

The broader OpenCoesione API/Projects/Soggetti surfaces remain blocked. PRR Projects and Mais Transparência remain permanently closed to the intelligence plane.

### 4.3 Other procurement/funding sources

A source that does not satisfy the pre-receipt zero-person contract remains disabled. Download-then-filter is prohibited. Silence or lack of contrary evidence is never permission. No human contact may be used to qualify a source.

## 5. Canonical customer objects

`FundingProject`, `PurchaseComponent`, `ProcurementEvidence`, `ComponentAssessment`, `ProjectAssessment` and the customer-safe `RunwayProject` read model remain the canonical contracts. Browser/API code may consume only the published customer-safe contract. Raw source transports, beneficiary identity, buyer/contact identity, unvalidated candidate text and intelligence-ledger credentials must not cross into the customer plane.

Every published evidence span is verbatim and offset-validated. Every published project is versioned and hash-anchored.

## 6. Matching and inference boundary

Production component extraction is deterministic and requires exact phrase evidence from the frozen taxonomy. The production path does not use a local model or LLM to create components, evidence or state.

CLOSED requires exact accepted TED evidence. A structurally plausible project-reference, CPV or geography candidate that cannot satisfy CLOSED is allowed to block OPEN and produce UNRESOLVED. Semantic similarity alone cannot create CLOSED or OPEN.

Any future reintroduction of inferred component semantics creates a new independent validation gate and cannot inherit the evidence-bounded approval.

## 7. Customer workflow

Authenticated customer routes are:

- `/app` — opportunities/runway feed;
- `/app/projects/[id]` — funded-project detail;
- `/app/components/[id]` — component evidence/history;
- `/app/market` — customer-safe market aggregates;
- `/app/profile` — organisation supplier profile;
- `/app/saved` — saved opportunities;
- `/app/account` — account/billing integration surface.

Public routes remain `/`, `/product`, `/methodology`, `/pricing`, `/login`, `/terms` and `/privacy`.

## 8. Customer workspace boundary

ProcRun's own workspace code accepts only opaque non-personal organisation tenant keys and non-personal buying-fit criteria. It provides tenant-isolated supplier profile persistence, deterministic relevance, saved opportunities, filtered CSV export, market aggregates with explicit missingness and complete workspace deletion.

Authentication and billing providers may later issue the capability used to enter this boundary, but ProcRun's intelligence/workspace contract does not require customer names, email addresses, phone numbers or external person IDs.

## 9. Customer-facing coverage copy

Customer surfaces must preserve the semantic equivalent of:

> **Coverage: TED. No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED as of DATE. This is a rule-bounded observation and does not establish absence outside TED or under different wording/classification.**

No customer-facing text may imply complete Portuguese or Italian national procurement coverage.

## 10. Website claims

Allowed after own-code closure is green:

- exact source-evidenced project/component wording;
- exact source-evidenced TED procurement matches;
- rule-bounded TED OPEN observations;
- historical cutoff/version reproducibility;
- deterministic supplier relevance;
- transparent coverage and missingness limitations.

Not allowed:

- `we know no procurement exists`;
- complete national procurement coverage;
- blanket `100% accurate` or `trust blindly` language;
- complete bill of materials;
- guaranteed discovery of every future purchase;
- probabilistic GO/NO-GO or win probability;
- person/contact intelligence;
- source, government or EU endorsement.

## 11. Packaging

Launch package remains **ProcRun Portugal — €149/month** unless later commercial evidence changes it. Packaging never overrides the source, privacy, evidence or release gates.

## 12. Historical Phase 0 and A21 treatment

Phase 0B/0C remain failed tests of the retired TED-only demand-extraction hypothesis and are not rewritten. Historical A21/A21a work remains provenance. The uncompleted independent human-gold A21 benchmark is not a production dependency and is never represented as passed.

## 13. Remaining implementation order

Own-code release readiness is established only by ordinary CI plus the dedicated live `infrastructure-closure` proof. Once both are green and the closure PR is merged, remaining work is presentation/cosmetic refinement and explicitly separate third-party integrations such as authentication, billing, merchant configuration, domain/TLS and deployment wiring.

Third-party integrations must still satisfy the permanent product/privacy/legal rules before activation.

## 14. Authoritative build decision

Only `docs/BUILD_GATES.md` may declare own-code closure green. The required final label is:

**BACKEND / INFRASTRUCTURE: GREEN — COSMETIC WEB WORK + THIRD-PARTY INTEGRATIONS ONLY.**

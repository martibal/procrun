# ProcRun build gates

Status: **OWN-CODE INFRASTRUCTURE CLOSURE — PASS REQUIRED BEFORE COSMETIC-ONLY PHASE**

This file is the authoritative current gate summary. Historical gate documents remain provenance; conflicts are resolved in favour of this file plus the specifically referenced current contracts.

## Permanent rules

- No human contact, permission request or source-owner outreach is permitted.
- No personal data may be collected, received, stored or processed by the intelligence plane.
- Download-then-filter is not a privacy mechanism.
- Blocked source surfaces remain blocked unless already-public evidence proves the strict source contract before receipt.
- Ambiguity must fail closed; a technical obstacle is a requirement to find a compliant design, not permission to weaken product/legal rules.

## A1-A20

**PASS.** The completed pre-web source, ingestion, evidence, persistence, backup, scheduling and delivery baseline remains accepted subject to the current evidence-bounded semantics below.

## A21 — historical inferential classification target

**RETIRED FROM THE PRODUCTION PATH; NEVER CLAIMED AS PASSED.**

The historical A21 design required an independently adjudicated final human gold standard. That final gold standard was not completed. Rather than self-grade the engine or lower the thresholds, ProcRun removes the inferential claim from production. See `docs/CLASSIFICATION_ENGINE_VALIDATION_GATE.md` and `docs/EVIDENCE_BOUNDED_PRODUCTION_SEMANTICS.md`.

## A21R — evidence-bounded production proof

**HARD RELEASE GATE.** Production semantics are source-verifiable:

- OpenCoesione `OperationLocalIdentifier` is logical identity; CUP is a match alias only;
- components require exact project-source spans from the frozen taxonomy;
- unmatched/no-component source wording => UNRESOLVED with verbatim customer-visible evidence;
- CLOSED requires exact accepted TED evidence;
- plausible unresolved TED candidates block OPEN;
- OPEN requires complete TED coverage and means only that no match satisfying ProcRun's frozen exact-evidence rules was found through the cutoff;
- customer output is PII-free, versioned and hash-anchored;
- three repeated builds from identical live inputs must be byte-equivalent by content hash;
- the real append-only PostgreSQL persistence path and customer JSONL write must succeed.

The dedicated `infrastructure-closure` workflow is the executable A21R proof. A commit is not release-green unless that workflow and ordinary CI both pass.

## Customer workspace core

**OWN CODE MUST PASS BEFORE COSMETIC-ONLY PHASE.**

ProcRun's provider-neutral web/control-plane code must provide:

- authenticated capability boundary expressed only as an opaque non-personal `org_<32 hex>` tenant key;
- no name, email, phone or external person/user identifier in ProcRun workspace storage;
- tenant-isolated supplier profile persistence containing only organisation buying-fit criteria;
- deterministic relevance that never mutates evidence/classification state;
- tenant-isolated Saved Opportunities;
- authenticated filtered customer-safe CSV export;
- Market Intelligence aggregates with explicit missingness and no unsupported market-size claim;
- complete workspace deletion independent of the immutable intelligence ledger;
- browser/API access only to the published customer-safe JSONL contract, never direct intelligence-ledger credentials.

Third-party authentication/billing implementation (for example Clerk or Stripe), merchant configuration, domains/TLS and visual/cosmetic work are separate integration/presentation phases and are not part of this own-code closure.

## Final decision rule

Only a commit where ordinary CI and the dedicated live infrastructure-closure proof are both green may be labelled:

**BACKEND / INFRASTRUCTURE: GREEN — COSMETIC WEB WORK + THIRD-PARTY INTEGRATIONS ONLY.**

Until that evidence exists, the label is prohibited.

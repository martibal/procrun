# Procurement Runway

Procurement Runway is a private, evidence-first procurement-intelligence product for suppliers to publicly funded infrastructure projects.

Its locked purpose is:

> **Find publicly funded projects, determine which purchasable components were already procured, and show customers only the components that still appear commercially open — with a dated evidence trail.**

The launch market is **Portugal**. Italy is the first planned expansion market, followed by Poland. The primary initial customer profile is civil-engineering, infrastructure, equipment and related specialist suppliers.

This repository contains the core data plane, procurement-coverage logic, component engine, append-only evidence ledger, local-model safety/benchmark boundary and the compliance controls that govern external data/services. The customer website is intentionally downstream of source legality, source safety and false-OPEN protection.

---

## 1. The problem

A funding announcement is not the same thing as a commercial opportunity.

A broad funding feed may tell a supplier that a large water, rail, port, energy-efficiency or resilience project has been funded. It does not answer the commercially important question:

> **Which parts of that project are still realistically left to buy?**

By the time a supplier discovers a funded project, some parts may already have been tendered, awarded or contracted. A naive `funded project = lead` product therefore creates dead leads and wastes sales effort.

Procurement Runway starts from a funded project, decomposes official scope into separately purchasable components, searches permitted procurement evidence backward to the analysis cutoff, and suppresses components for which relevant procurement already existed.

The atomic product object is therefore not a tender and not simply a funded project. It is a:

> **dated funding-to-procurement coverage ledger at component level.**

---

## 2. What the product is — and is not

### It is

- an incremental coverage process for publicly funded infrastructure projects;
- a component-level ledger of what appears already procured versus still commercially open;
- a dated evidence product with reproducible source provenance;
- a conservative filtering layer that deliberately removes questionable/dead leads;
- a system that can later connect newly published procurement back to an earlier signal and measure actual lead time.

### It is not

- a generic TED or Portal BASE tender-search interface;
- a feed of every funded project;
- a bid-writing/proposal-generation product;
- a CRM;
- a contact-person or supplier-person database;
- a win-probability model;
- an "AI says this will be tendered" product;
- a claim that no procurement exists when only bounded indexed-source searches were performed;
- a system optimised for maximum lead volume.

Product value comes partly from **withholding and suppressing** weak opportunities.

---

## 3. Locked governing decisions

Product Requirements v1.0 was approved for core development on 1 September 2026. Implementation must not silently weaken these decisions:

| Decision | Locked value |
| --- | --- |
| Launch market | Portugal |
| Phase 2 | Italy, then Poland |
| Primary ICP | Civil engineering / infrastructure suppliers |
| Product object | Component-level funding-to-procurement coverage ledger |
| Worst error | False `OPEN` |
| External LLM in analytical path | Not permitted in MVP |
| Natural-person data in intelligence plane | Not permitted |
| Early infrastructure target | NOK 400/month |
| Early infrastructure absolute stop | NOK 500/month |
| History | Append-only/versioned |
| Outcome tracking | Starts from first live signals |

Changing the product promise, PII boundary, classification semantics or launch-country scope requires an explicit Product Requirements review.

---

## 4. Evidence baseline: Phase 0 V1.1

The preregistered Phase-0 test covered 30 public-infrastructure projects. Corrected V1.1 result:

- **18 CLOSED**
- **6 OPEN**
- **4 PARTIAL**
- **2 UNRESOLVED**
- **93.3% resolved**
- **60.0% dead-lead suppression**
- **33.3% OPEN/PARTIAL retained**
- **13.3% PARTIAL**
- **20/30 (66.7%) removed or withheld versus a naive funding feed**
- separately corroborated lead-time cases of **301 days** and **364 days**

Frozen preregistration SHA-256:

`aebfd33597697c7ad33f32e3e19a95b02c9ef683390d35ac4fa348d0fa591ef4`

Critical regression case: `PACS-FC-04022300` must remain `PARTIAL`, not `OPEN`.

The evidence validates the public-infrastructure/equipment/engineering wedge; it does not establish every procurement vertical.

---

## 5. State semantics

### `FUNDED`

Public funding for the project is documented.

### `COMPONENT`

A separately purchasable work, service or equipment category derived from official project scope.

### `CLOSED`

Relevant procurement existed at or before cutoff and demonstrably covers the component. Suppress the component as a customer opportunity; retain evidence/history.

### `OPEN`

Required indexed-source coverage completed and no relevant procurement was found for the component at or before cutoff.

Customer wording must remain bounded:

> **No relevant procurement found in indexed sources as of DATE.**

`OPEN` never means that Procurement Runway has proven procurement does not exist.

### `UNRESOLVED`

Evidence is insufficient, source coverage incomplete, component boundary ambiguous, or the match is not strong enough to decide safely. Withhold rather than guess.

### `PARTIAL`

A project contains different component states. Only qualifying OPEN components may be surfaced. CLOSED is retained as history/evidence and UNRESOLVED remains withheld.

### `OUTCOME`

A later tender/award linked back to the original component signal, retaining original publication time and observed `lead_days`.

---

## 6. Core error policy

**False `OPEN` is the worst product error.**

Therefore:

- ambiguity between OPEN and CLOSED/PARTIAL becomes `UNRESOLVED` or `PARTIAL`;
- incomplete source coverage can never support `OPEN`;
- semantic similarity alone can never establish `CLOSED`;
- feed volume is never a reason to relax evidence thresholds;
- no generative model may infer absence of procurement.

This asymmetry is deliberate: withholding a real opportunity is less damaging than selling a customer an already-dead one.

---

## 7. End-to-end processing pipeline

1. **Detect** — identify newly visible/changed funded projects from an approved Portugal 2030 route.
2. **Normalize** — map the source record to strict canonical schema; reject unexpected fields.
3. **Temporal provenance** — record defensible public `first_seen_at`; never substitute project start date.
4. **Component decomposition** — deterministic phrase/rule extraction first.
5. **Local-model fallback** — only unmatched approved scope spans may be shown to a pinned local model; model proposes taxonomy labels + exact spans only.
6. **Search backward** — query approved procurement sources at/before cutoff.
7. **Candidate matching** — compare identifiers, dates, authority, geography, CPV/category and scope evidence.
8. **Classify component** — `CLOSED`, `OPEN` or `UNRESOLVED`.
9. **Derive project state** — preserve mixed projects as `PARTIAL`.
10. **Persist evidence** — append immutable source/evidence/classification versions and hashes to PostgreSQL.
11. **Publish** — expose only qualified OPEN/PARTIAL components with dated evidence/coverage statement.
12. **Track forward** — connect later procurement to original signals.
13. **Backtest** — accumulate observed precision, false-OPEN corrections and lead time.

---

## 8. Source approval model

A source is not production-safe merely because it is public. Three independent gates must be green:

1. **RIGHTS** — commercial reuse/derivative use is permitted.
2. **ACCESS** — automated access is permitted through the exact route, including authorization/rate conditions.
3. **DATA SAFETY** — prohibited person/supplier fields can be excluded **before receipt**.

The executable registry is `src/procrun/source_contracts.py`. `require_live_source()` must run before live retrieval. Approved reviews have an expiry date; stale reviews fail closed.

Current status:

| Route | Overall | Rights | Access | Data safety |
| --- | --- | --- | --- | --- |
| TED Search API | APPROVED | APPROVED | APPROVED | APPROVED |
| Mais Transparência project search | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Mais Transparência project detail | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED |
| PT2030 operations bulk workbook | BLOCKED | CONDITIONAL | APPROVED | BLOCKED |
| Portal BASE / APIBase2 | BLOCKED | CONDITIONAL | CONDITIONAL | BLOCKED |

See [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md) and [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md).

### TED

TED is currently the cleanest production source. The Search API explicitly supports analysis/reuse and names commercial value-added platforms as intended users. TED notices can be reused commercially unless otherwise noted. ProcRun uses only the field-projected public API, not CMS scraping/full XML ingestion.

Operational/compliance rules include:

- explicit projected fields only;
- no buyer contact, email, phone, supplier/winner or personal-address fields;
- schema drift fails closed;
- internal request ceiling below TED's published fair-use ceiling;
- future customer source pages credit TED/EU, disclose transformation/classification, do not imply EU endorsement and do not distort source meaning.

### Portugal 2030 / Mais Transparência

The portal is useful for human research but is **not** an approved production HTML-scraping contract. Full detail contains beneficiary content and is blocked.

The dados.gov.pt PT2030 operations workbook is also blocked: download-then-filter violates the pre-receipt zero-PII rule. Its current dataset metadata says `Licença não especificada`; the repository therefore does not promote source-specific rights to unconditional APPROVED merely from dados.gov.pt's portal-wide default CC BY 4.0 rule.

The remaining core blocker for Portugal is a field-bounded official/open-data transport that simultaneously provides required scope, excludes prohibited fields before receipt, has defensible rights/access, and supports temporal first-seen provenance.

### Portal BASE / IMPIC

Portuguese rules permit automated extraction of public BASE data, but large-volume API access requires registration/prior IMPIC authorization. The documented API returns broad fields including `adjudicatarios` identifiers/names and does not document server-side output projection. APIBase2 therefore remains blocked even if an API token becomes available.

---

## 9. Zero-PII intelligence boundary

No natural-person data may enter the intelligence pipeline, database, model context, application logs or customer intelligence output.

Critical rule:

> **Do not download a broad response containing prohibited fields and discard them afterwards.**

If a source cannot prevent prohibited data from entering the response, the route is blocked.

Allowed project field classes include operation code, title, audited scope text, funding/executed amount, planned dates, programme/fund/objective/theme and geography. Beneficiary legal-entity name is conditional only when the schema positively establishes an organisation.

Prohibited project fields include beneficiary NIF/NIPC, natural-person beneficiary, email, phone, contact person and signature.

Allowed procurement fields include notice/procedure ID, dates, title/scope, CPV, procedure/contract type, values, geography and contracting-authority organisation name.

Supplier/adjudicatário, contact person, email, phone and personal address are explicitly excluded in MVP.

Enforcement:

- hard-coded allowlists;
- unknown keys fail before persistence;
- raw HTTP bodies are not persisted;
- logs contain identifiers/status/counts/hashes/timings, not raw values;
- no full-page HTML archive;
- model context is built only from already-approved fields;
- no analytics/session replay/advertising trackers in MVP.

A public web service necessarily transmits client IP through network infrastructure. The guarantee applies to ProcRun application persistence/logs/models/customer datasets; the app itself must not persist client IP.

---

## 10. Temporal provenance

`first_seen_at` means defensible first public observability, not project start date.

Historical backfills without defensible source snapshot dates remain `temporal_provenance=UNRESOLVED` and cannot support historical lead-time claims. For newly observed records, local observation time may become valid first-seen provenance once the discovery transport itself is approved.

---

## 11. Component engine

Initial fixed taxonomy covers:

- water/wastewater;
- rail/transport;
- ports/coastal;
- energy efficiency;
- resilience/fire.

Deterministic rules run first and preserve exact source spans. Duplicate/overlapping components are canonicalised before matching. Unmatched scope is retained as explicit unresolved/fallback work; it is never interpreted as "no component".

The local model is a parser fallback, not a procurement decision-maker.

---

## 12. Local-model boundary

Current benchmark candidate: **Qwen3-4B Q4_K_M**.

- model licence reviewed as Apache-2.0;
- exact repository revision/file/size/SHA-256 pinned;
- llama.cpp exact benchmark commit pinned;
- local/offline inference only;
- fixed resource/time bounds;
- model sees only unmatched allowlisted spans and frozen category choices;
- model output may propose component/category + exact supporting span only;
- model cannot set `OPEN`, `CLOSED`, `PARTIAL` or `UNRESOLVED`;
- every proposal/cached result is revalidated against source spans/categories.

The model remains `BENCHMARK_CANDIDATE`, not production-approved. Production promotion requires empirical quality/RAM/latency evidence on the target host and an explicit registry decision.

---

## 13. Procurement matching

The conservative hierarchy is qualitative because Product Requirements v1.0 did not freeze a numeric score threshold.

- **Tier A:** exact project/funding identifier + component scope + compatible date. Exact project ID alone does not close every component.
- **Tier B:** contracting authority + geography + high scope overlap + CPV/category + compatible date.
- **Tier C:** title/location + scope + CPV/category + date + corroborating amount/date. Current implementation treats this as review-quality, therefore `UNRESOLVED` rather than inventing a numeric CLOSED threshold.
- **Tier D:** semantic similarity only. Never sufficient for CLOSED.

A high-confidence A/B pre-cutoff match closes a component even if another required source is temporarily incomplete. Conversely, absence can become OPEN only when required coverage is complete.

---

## 14. Evidence ledger

PostgreSQL 16 is the canonical historical ledger.

The ledger stores immutable versions for:

- source records and retrieval observations;
- funding projects;
- components;
- procurement evidence;
- component/project assessments;
- later outcomes;
- run manifests.

Corrections append a new version with explicit supersession. Database triggers reject UPDATE/DELETE on ledger tables. Every persisted content object is hash-bound and every daily run has a manifest.

See [`docs/LEDGER.md`](docs/LEDGER.md).

---

## 15. Intended customer product

The MVP should feel like a qualified opportunity ledger, not a procurement portal.

Planned customer surfaces:

- **Opportunity feed:** OPEN/PARTIAL projects only; filter by component, region, funding size, project end date/status.
- **Project detail:** funding evidence, component ledger, already-procured evidence, remaining OPEN components, as-of date and source links.
- **Track record:** later outcomes and observed lead-time statistics once enough history exists.
- **Pull-based delivery:** RSS/Atom/API/CSV/JSON using permitted intelligence fields only.

No generic tender search, contact database or bid-writing feature is part of MVP.

---

## 16. Website/control-plane release gates

The future customer website creates a separate PII/commercial control plane. Before paid launch it must have:

- final legal entity/merchant identity;
- customer Terms of Service/subscription terms;
- Privacy Notice covering account, billing, support and unavoidable network processing;
- processor/subprocessor inventory and required DPAs;
- Stripe/payment account approval plus VAT/invoicing/refund/subscription design;
- source attribution/methodology page using then-current approved source obligations;
- no analytics/session replay/advertising SDK by default;
- account/billing/support data separated from the procurement intelligence ledger/model;
- application/reverse-proxy logging configured not to persist client IP in the ProcRun data plane;
- TLS, secrets, least privilege, encrypted backups and restore procedure;
- short external legal review of then-current Portuguese source rights/attribution and customer-facing terms.

Stripe is currently `CONDITIONAL`, not active. Cloudflare is optional/`CONDITIONAL` and should not be introduced without a concrete need and new review.

---

## 17. Third-party software and service compliance

See [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

Direct runtime dependencies are exact-version pinned. `requirements-runtime.lock` constrains the reviewed Python 3.12/Linux runtime dependency closure so transitive package drift cannot silently alter the reviewed software surface.

Key licences include:

- httpx/httpcore — BSD-3-Clause;
- Psycopg/Psycopg Binary — LGPL-3.0-only;
- Pydantic/Pydantic Core — MIT;
- certifi — MPL-2.0;
- Qwen3-4B-GGUF — Apache-2.0;
- llama.cpp — MIT;
- PostgreSQL — PostgreSQL License.

Current external-service roles:

- **GitHub:** approved for private source + CI, not production intelligence storage.
- **Hetzner:** approved for normal EU hosting and ephemeral benchmarks.
- **Hugging Face:** approved only for download of the exact pinned public model artifact; hosted inference is not approved.
- **Stripe:** conditional future payment/control-plane service.
- **Cloudflare:** conditional optional DNS/CDN/DDoS layer.

Compliance reviews intentionally expire. Current review date is 2026-09-01; current due date is 2026-11-30. CI/runtime gates are intended to fail after expiry until terms are rechecked.

---

## 18. Technical architecture

Locked early topology:

- Python 3.12;
- FastAPI later for API/server-rendered web surface;
- PostgreSQL 16 + `pg_trgm`/full-text;
- systemd timers/cron for jobs;
- local llama.cpp-compatible 3–4B quantized multilingual model;
- no external LLM API in MVP analytical path;
- no paid data API;
- one EU VPS initially: API/UI + worker + PostgreSQL + local NLP;
- compressed append-only evidence/manifests rather than raw payload lake;
- nightly encrypted PostgreSQL backup to EU target;
- self-hosted health/local counters;
- no analytics/session replay/ads SDK.

The desired server class is Hetzner CX33 (4 vCPU / 8 GB RAM / 80 GB), subject to the benchmark. If inference cannot fit safely, optimise rules/caching/batching before automatically scaling the whole architecture.

---

## 19. Cost discipline

Core recurring infrastructure:

- target: **<= NOK 400/month**;
- absolute early-stage stop: **NOK 500/month**.

If projected trailing-30-day core infrastructure spend exceeds NOK 400, raise a warning. No recurring resource change may push projected spend above NOK 500 without an explicit architecture decision.

Variable commercial costs such as payment-processing fees are tracked separately from the core infrastructure ceiling.

The core cost strategy is `compute once, serve many`: project/component classification is canonical product state, not recomputed independently for every customer.

---

## 20. Local disk policy

The repository contains code and small fixtures only. Raw datasets, caches, databases, model weights, exports and downloaded archives are ignored by Git.

Default local runtime budget: **20 GiB**. Production historical state belongs on the EU server. Development PostgreSQL is disposable and has no persistent host volume.

This keeps local storage bounded even though the workstation itself may have limited disk.

---

## 21. Current implementation status

Implemented and regression-tested before this compliance hardening round:

- strict domain models and PII/unknown-field boundary;
- source approval gate;
- field-projected TED collector;
- Portal BASE hard block;
- append-only PostgreSQL ledger;
- Phase-0 V1.1 regression oracle;
- conservative matching engine;
- five-domain deterministic component engine + exact spans;
- local-model request/response safety contract;
- pinned Qwen benchmark candidate and llama.cpp runtime;
- synthetic pt-PT benchmark corpus;
- one-command benchmark runner;
- ephemeral Hetzner benchmark provisioning/cleanup automation;
- CI with shell/PowerShell syntax, Ruff, strict mypy, pytest and PostgreSQL integration.

This compliance round adds:

- separate RIGHTS / ACCESS / DATA SAFETY gates;
- source/provider/model review expiry;
- explicit TED attribution/fair-use obligations;
- conservative PT2030 source-specific licence handling;
- dependency/provider compliance registry;
- exact direct-runtime versions and frozen runtime transitive constraints;
- pre-network/pre-billable compliance checks in benchmark provisioning/download paths;
- detailed source/provider/customer-release compliance documentation.

Still intentionally blocked/open:

1. **Portugal 2030 production discovery route** — must be legally cleared, automation-safe, field-bounded, zero-PII and temporally defensible.
2. **PT2030 source-specific licence clarification** for the currently "licence unspecified" bulk dataset (which remains data-safety blocked regardless).
3. **Portal BASE** — current API response surface remains blocked; future use also requires IMPIC authorization/terms.
4. **Local-model production approval** — target-host benchmark must pass before promotion.
5. **Shadow run** — continuous Portugal outcomes must accumulate before strong performance claims.
6. **Customer website/control plane** — privacy, terms, attribution, organisation entitlement and payments are release gates.

---

## 22. Build sequence

- **Phase A — data plane:** canonical schemas, source adapters/gates, allowlists, temporal provenance, PostgreSQL ledger.
- **Phase B — procurement coverage:** TED, approved national source, candidate matching/classification.
- **Phase C — component engine:** taxonomy, deterministic extraction, local-model fallback, exact spans, regression suite.
- **Phase D — shadow run:** continuous Portugal operation/outcome accumulation.
- **Phase E — customer MVP:** minimal web feed/project pages, pull-based outputs, organisation entitlement.
- **Phase F — expansion:** Italy first (CUP→CIG), then Poland. Spain remains conditional until linkage gate passes.

---

## 23. Development

Python 3.12+ and Docker are recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -c requirements-runtime.lock -e ".[dev]"
docker compose up -d db
```

Windows integration-test DB:

```powershell
$env:PROCRUN_TEST_DATABASE_URL="postgresql://procrun:procrun-local-only@127.0.0.1:5432/procrun"
pytest
```

Remove disposable local DB when finished:

```bash
docker compose down
```

CI runs compliance checks, shell/PowerShell syntax, Ruff, strict mypy, pytest and PostgreSQL 16 integration.

---

## 24. Target-model benchmark

The benchmark is separate from production approval. The Windows end-to-end runner can:

1. create an ephemeral Hetzner CX33 host;
2. wait for cloud-init;
3. transfer only committed repository content;
4. build the pinned llama.cpp revision;
5. download and verify the pinned Qwen GGUF;
6. run the frozen synthetic benchmark corpus;
7. retrieve the result bundle locally;
8. delete the server only after results are safely copied.

If execution fails, the server is intentionally retained for diagnostics and must be explicitly deleted to stop billing. Model files/results stay outside Git.

---

## 25. Rules for future contributors

Do not:

- activate a source because it is merely public;
- download broad data and filter prohibited fields afterwards;
- scrape a presentation site when a safer approved data route is required;
- add supplier/contact-person data to improve matching;
- use project start as first-seen provenance;
- let an LLM decide procurement state;
- turn missing evidence into OPEN;
- change bounded OPEN wording to an absolute claim;
- overwrite ledger history;
- add paid LLM/data APIs as the first scaling response;
- add managed services without provider/privacy/cost review;
- add runtime dependencies without licence/lock review;
- commit raw datasets, model weights, secrets, production DBs or customer data;
- expand geography before Portugal source/outcome gates are stable.

Do:

- fail closed on uncertainty;
- preserve exact source/evidence provenance;
- prefer deterministic rules and caching;
- treat rights, access and data safety as separate gates;
- keep customer/account PII separate from the intelligence plane;
- update compliance dates/evidence deliberately when terms change.

---

## 26. Key repository documents

- [`docs/BUILD_GATES.md`](docs/BUILD_GATES.md) — non-negotiable engineering/release gates.
- [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md) — current source decisions/transport contracts.
- [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) — source rights, provider terms, licences and customer-control-plane release gate.
- [`docs/LEDGER.md`](docs/LEDGER.md) — append-only PostgreSQL/evidence model.
- [`docs/MATCHING_RULES.md`](docs/MATCHING_RULES.md) — conservative candidate/classification rules.
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) — reviewed software/model licence notes.
- [`requirements-runtime.lock`](requirements-runtime.lock) — frozen production runtime dependency closure.

Product Requirements v1.0 and corrected Phase-0 V1.1 evidence remain governing product artifacts. This README is intended to let a new person understand the repository without prior conversation, but it does not supersede those locked artifacts.

---

## 27. Bottom line

Procurement Runway is building an evidence-backed answer to a deliberately narrow question:

> **For a funded infrastructure project, what is still plausibly left to procure?**

The evidence so far shows that naive funding feeds contain substantial dead-lead noise and that component-level treatment matters. The architecture therefore intentionally ingests less, preserves provenance, uses deterministic logic wherever possible, uses local AI only as a bounded parser, suppresses ambiguity, keeps history immutable, keeps source rights/access explicit, and holds early infrastructure below a hard cost ceiling.

The most important remaining blocker is **not the website**. It is obtaining a Portugal 2030 production discovery route that is simultaneously **legally cleared, automation-safe, field-bounded, zero-PII and temporally defensible**. Until that gate is green, the engine can be tested and hardened, but the project must not pretend the Portugal production data plane is complete.

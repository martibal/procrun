# Portugal 2030 discovery — final source-resolution gate

Status date: 2026-09-03.

## Decision

**Portugal 2030 funded-project discovery remains NOT PRODUCTION-APPROVED.**

After a final source-resolution pass across the national portal, the national open-data catalogue, the Portugal 2030 results publication and programme-level managing-authority surfaces, no official route was established that satisfies all ProcRun launch gates simultaneously.

The blocking combination is unchanged:

1. current/national project coverage;
2. sufficiently rich project-specific scope for exact component evidence spans;
3. field-bounded transport that excludes prohibited beneficiary/person/supplier fields before receipt;
4. commercial reuse and automated-access terms for the exact transport;
5. defensible first-seen provenance and fail-closed schema control.

ProcRun must not weaken the zero-PII boundary to solve this.

## Candidate A — Mais Transparência Portugal 2030 project search/detail

Official current portal material continues to show a national Portugal 2030 project search with project title, operation code, completion date and financing amount. The portal identifies AD&C as the source and states that portal information is updated from data made available through the national open-data ecosystem.

The search-card surface remains materially safer than project detail, but it is insufficient for the normal component engine because it does not provide the project `Sumário` / rich scope text. A title-only mode remains research-only and cannot infer components beyond exact title spans.

The project-detail surface provides the required `Sumário`, but beneficiary information is part of the same public project response/surface. No authoritative current documentation was found for a separate server-side field projection that can return the rich project scope while excluding beneficiary/person fields before receipt.

Decision:

- national/current discovery: **PASS**
- card-level pre-receipt safety: **PROMISING / UNVERIFIED**
- normal rich-scope sufficiency from cards: **FAIL**
- rich-scope field-bounded transport: **FAIL / NOT ESTABLISHED**
- exact-route commercial automated-access contract: **CONDITIONAL / NOT FROZEN**
- production eligibility: **REJECTED**

No new project-detail body or beneficiary record was fetched during this final-resolution pass.

## Candidate B — dados.gov.pt API

The official dados.gov.pt API documentation describes the catalogue API, pagination and read/write behaviour. It demonstrates retrieval of catalogue objects and directs users to API/reference documentation. The documented examples do not establish an operation-row endpoint with server-side output-column projection for the Portugal 2030 approved-operations resource.

The known PT2030 operations distribution remains a broad workbook. It contains useful operation identity/scope fields together with beneficiary fields/identifiers, so download-then-filter is prohibited.

Decision:

- official open-data catalogue: **PASS**
- metadata automation: **PASS**
- field-bounded PT2030 operation-row transport: **FAIL / NOT ESTABLISHED**
- broad workbook pre-receipt safety: **FAIL**
- production eligibility: **REJECTED**

No workbook body or operation row was fetched.

## Candidate C — Portugal 2030 national results publication

The official Portugal 2030 results page continues to publish a current national `Lista de Operações Aprovadas Portugal 2030` as an Excel download. This confirms that a national authoritative operations publication exists and is updated on a reporting cadence.

The publication route is still file-distribution, not a documented field-projected project API. It therefore does not solve the pre-receipt boundary already identified for the approved-operations workbook.

Decision:

- national/current coverage: **PASS**
- authoritative provenance: **PASS**
- field-bounded transport: **FAIL / NOT ESTABLISHED**
- download-then-filter: **PROHIBITED**
- production eligibility: **REJECTED**

No Excel body was fetched.

## Candidate D — programme / managing-authority surfaces

Current programme sites, including Sustentável 2030, expose public calls and associated project information, while programme/result sites also publish approved-operation lists. These surfaces are useful for human research but do not establish a single national alternative architecture for Portugal: no authoritative Portugal-wide machine-enumerable project feed with a documented field projection and rich-scope zero-PII guarantee was identified.

A federation of programme websites would also introduce completeness, schema, rights/access and temporal-provenance problems before the privacy gate is even considered.

Decision:

- official programme provenance: **PASS**
- Portugal-wide completeness boundary: **FAIL / NOT ESTABLISHED**
- single frozen schema/transport: **FAIL / NOT ESTABLISHED**
- production eligibility: **REJECTED**

No programme project row, attachment or project-detail body was fetched.

## Final product gate

Portugal remains the locked launch market, but **live funded-project discovery is blocked by source feasibility, not by missing implementation work**.

The core engine may continue to be developed and tested using permitted synthetic/frozen fixtures. A live Portugal collector must not be created from any route above.

### Reopen only on new authoritative evidence

Portugal discovery research should now be **CLOSED BY DEFAULT** for the currently known source families. Reopen only if an official source or contract establishes all of the following:

- current Portugal 2030 project coverage with a machine-testable completeness boundary;
- project ID/title, funding/programme/geography/dates and sufficiently rich project-specific scope;
- server-side output projection or an independently safe distribution that prevents prohibited beneficiary/person/supplier fields from entering the response;
- explicit pre-publication zero-PII assurance for any retained free-text scope;
- commercial reuse and automated-access terms for the exact route;
- defensible `first_seen_at` provenance;
- a frozen schema/allowlist with fail-closed drift handling.

Until then, the product must not substitute local filtering, page scraping, broad workbook downloads or beneficiary-containing project-detail responses for a safe source contract.

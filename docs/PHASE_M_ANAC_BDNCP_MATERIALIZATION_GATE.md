# Phase M — ANAC/BDNCP materialization gate

Status: **BLOCKED — NO QUALIFYING PRE-RECEIPT CUP→PROCUREMENT PROJECTION**

Reviewed: 2026-09-12

## Purpose

After the frozen 12-month OpenBDAP MOP cohort was created, ProcRun tested TED as the prospective procurement-materialization layer. The preregistered TED structured-CUP route returned zero matches in the frozen qualification sample and was closed as `BLOCKED_NO_STRUCTURED_CUP_EVIDENCE`.

The next candidate is ANAC / BDNCP because CUP and CIG are authoritative Italian public-investment / procurement identifiers and ANAC publicly exposes procurement lifecycle information.

This gate asks one narrow question:

> Can ProcRun obtain procurement materialization for a supplied CUP through an already-public, machine-usable route that constrains the response **before receipt** to a frozen non-PII field allowlist?

The answer on the public evidence reviewed on 2026-09-12 is **no**.

## Permanent constraints

**“Datasikkerheten følger ikke av at kilden er offentlig, den følger av hva vi faktisk lar systemet motta.”**

ProcRun therefore does not permit:

- downloading a broad BDNCP/CKAN resource and filtering locally;
- receiving full PVL search-result or detail payloads and deleting unsafe fields afterwards;
- scraping rendered notices as an intelligence-ingest mechanism;
- receiving RUP/contact/person/party fields and discarding them after receipt;
- prohibited: bespoke extraction or clarification via ANAC;
- treating public availability as equivalent to a pre-receipt safety contract.

## Public evidence established

### 1. CUP exists in the public procurement surface

The official ANAC Pubblicità a Valore Legale manual documents keyword search that may use CIG, CUP, contracting authority and other terms. The same manual documents CUP as a field shown in procurement-detail data together with CIG and other procurement attributes.

This establishes that CUP can occur in the ANAC publication surface. It does **not** establish a safe machine projection.

### 2. Public BDNCP access exists

ANAC states that BDNCP provides free public access to public-contract data and that the open-data / analytics surface can be searched by CIG. ANAC also states that BDNCP lifecycle data are publicly consultable.

This establishes public access. It does **not** establish a CUP-filterable, server-side field-projected API suitable for ProcRun.

### 3. Historical ANAC–DIPE documentation confirms CUP↔CIG association exists conceptually

Public ANAC/DIPE technical documentation states that contract data can be made available for records where CUP and CIG can be associated.

This supports the semantic validity of CUP↔CIG linkage, but the described exchange is an institutional integration and is not evidence of an unrestricted public API contract available to ProcRun.

### 4. Existing ProcRun CKAN qualification did not close the route

ProcRun's existing metadata-only probe targets `https://dati.anticorruzione.it/opendata/api/3/action/package_show` and deliberately does not download resource bodies. Earlier qualification work did not establish a stable field-level pre-receipt projection route; the CKAN metadata route was not sufficient to approve live BDNCP row ingestion.

## Gate assessment

| Gate | Result | Reason |
|---|---|---|
| Semantic CUP↔CIG relevance | PASS | Public ANAC material establishes CUP/CIG association in procurement data. |
| Public human-readable access | PASS | PVL / BDNCP are publicly accessible. |
| Machine access suitable for ProcRun | NOT PROVEN | No qualifying public CUP→procurement API contract has been established. |
| Server-side CUP filter | NOT SUFFICIENTLY PROVEN | PVL documents human-facing CUP search, not a frozen machine API request contract. |
| Server-side field projection | FAIL / NOT PROVEN | No authoritative public `fields`, `$select`, projection or equivalent output-boundary contract was found for the CUP route. |
| Zero-PII before receipt | **FAIL** | Without a proven output projection, ProcRun cannot guarantee that only safe fields are received. |
| Human-contact-free closure | PASS | The route is blocked; no human-dependent escalation is permitted. |

## Decision

`ANAC_BDNCP_MATERIALIZATION = BLOCKED_NO_PRE_RECEIPT_PROJECTION`

No live ANAC procurement rows may be ingested for the Phase-M MOP prospective cohort under the current evidence.

The existing `anac-cig-metadata` workflow remains diagnostic/manual only. It must not be converted into a row-ingest workflow merely because BDNCP data are public.

## What could legitimately reopen this gate

Only new **already-public** authoritative evidence can reopen the gate. It would need to establish all of the following without human clarification:

1. a public machine endpoint;
2. server-side filter semantics accepting CUP or an equivalently deterministic safe identifier;
3. an explicit server-side output projection mechanism;
4. a frozen allowlist that excludes natural-person, contact, party and uncontrolled free-text fields before receipt;
5. automated-access and reuse terms compatible with ProcRun;
6. schema / contract behaviour that can fail closed on drift.

Until all six are evidenced, the route stays blocked.

## Phase-M consequence

At this point:

- OpenBDAP MOP prospective cohort: **FROZEN / CONDITIONAL GO**;
- TED structured CUP materialization: **BLOCKED — zero structured CUP evidence in preregistered sample**;
- ANAC/BDNCP CUP materialization: **BLOCKED — no qualifying pre-receipt projected route**.

This does **not** prove that the 1,356 MOP cohort projects never procure. It means ProcRun currently lacks an approved, zero-PII materialization source that can observe that outcome prospectively.

The next candidate must therefore be a different already-public procurement source with an explicit machine projection contract. ProcRun must not weaken the safety boundary to force a linkage result.

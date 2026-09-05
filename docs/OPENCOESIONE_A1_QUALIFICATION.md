# OpenCoesione A1 source qualification

Status: **APPROVED SOURCE CONTRACT — EXACT 2021-2027 EU COHESION OPERATION-LIST ROUTE ONLY**
Runtime activation status: **PR FESR Lombardia 2021-2027 ONLY; OTHER SAME-FAMILY ROUTES REQUIRE SEPARATE TECHNICAL ACCEPTANCE**
Review date: 2026-09-05

This decision applies only to the bounded public ZIP/CSV operation/beneficiary lists published by OpenCoesione for EU-funded national and regional 2021-2027 programmes. It does **not** approve the general OpenCoesione API, Projects database, Soggetti/entity datasets, project-detail HTML, or any broader route.

## Permanent validation constraint

Source qualification is public-evidence-only and has no human-dependent fallback. If already-public evidence cannot close a source contract, the route is rejected or blocked. No future activation step depends on a reply, permission, assurance or bespoke interpretation from a source owner or other person. All candidate routes fail-closed until their exact technical contract is independently established.

## Approved source family

- publisher: OpenCoesione / MEF-RGS-IGRUE;
- publication: `Lista beneficiari e operazioni 2021-2027`;
- programme universe: all national and regional 2021-2027 programmes financed with EU funds, exactly as represented by the publisher's operation-list page;
- refresh claim: bimonthly;
- licence: CC BY 4.0, including commercial reuse with attribution;
- beneficiary identity is not admitted to ProcRun's canonical `FundingProject` analytical object.

Source-family approval does not activate every programme route. Runtime activation requires exact route acceptance plus evidence sufficient to establish the frozen transport schema before ProcRun receives row-bearing data.

## Privacy and free-text contract

The RGS/ReGiS publication rule for `TITOLO_PROGETTO` and `SINTESI_PROG` states that project title/summary must not contain information attributable to natural persons, including name, tax code, telephone number or email address. This is a **data-provider instruction and publication rule, not a technical database constraint**; the residual risk is therefore documented rather than described as impossible.

For the 2021-2027 beneficiary/operation publication surface, OpenCoesione states beneficiary name is published **only for legal persons**. The public metadata workbook also describes masking behavior for natural-person beneficiary identity. ProcRun nevertheless excludes beneficiary identity fields from the canonical/customer-safe object.

Authoritative public evidence:

- `https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/`
- `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls`
- `https://opencoesione.gov.it/en/licenza/`
- `https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`
- `https://opencoesione.gov.it/media/uploads/linee-guida_comunicazione-e-opencoesione_v2_0.pdf`

## Frozen runtime schema

The live-approved Lombardia CSV transport contains 20 ordered columns, frozen in `src/procrun/collectors/opencoesione.py` as `EXPECTED_HEADERS`. Missing, renamed, reordered or additional columns fail before row admission.

OpenCoesione's central 2021-2027 beneficiary page links `metadati_beneficiari.xls`. The schema-only CI qualification on 2026-09-05 downloaded **38,400 bytes / 37.5 KiB**, matching the repeated 37.5 KB metadata-file signal that motivated the full-family check. The workbook is a 17-field regulatory/metadata model and is **not exact-equal** to the 20-column Lombardia runtime transport contract.

Exact frozen runtime names absent from the workbook under those exact names:

- `CostoTotale_TotalCost`
- `Ciclo_Period`
- `ObiettivoSpecifico_SpecificObjective`
- `DataInizioOperazione_OperationStartDate` — workbook uses `DataInizioProgetto_OperationStartDate`
- `DataFineOperazione_OperationEndDate` — workbook uses `DataFineProgetto_OperationEndDate`
- `Paese_Country` — workbook uses `StatoMembro_Country`

Therefore identical 37.5 KB schema-document size is not sufficient to prove equality with ProcRun's actual frozen runtime schema. This also corrects the premise that the collector itself freezes 17 fields: the regulatory metadata has 17 fields; the production collector freezes **20 transport columns**.

## Per-route qualification — 2026-09-05

The same authoritative OpenCoesione metadata workbook is linked from the central 2021-2027 beneficiary/operation publication and governs the family-level schema documentation. Each candidate is recorded separately because runtime activation is route-specific.

| Candidate route | Schema document | Exact comparison with frozen 20-column runtime contract | Runtime decision |
| --- | --- | --- | --- |
| Beneficiari dei Programmi 2021-2027 — all-program ZIP | `https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls` | FAIL — 17-field metadata model; six frozen runtime names absent/different | NOT ACTIVATED |
| PR FESR FSE+ Puglia | same official metadata workbook | FAIL — same exact mismatch | NOT ACTIVATED |
| PR FESR Campania | same official metadata workbook | FAIL — same exact mismatch | NOT ACTIVATED |
| PR FESR Lazio | same official metadata workbook | FAIL — same exact mismatch | NOT ACTIVATED |
| PR FESR Emilia-Romagna | same official metadata workbook | FAIL — same exact mismatch | NOT ACTIVATED |
| PR FESR Liguria | same official metadata workbook | FAIL — same exact mismatch | NOT ACTIVATED |
| PR FESR Veneto | same official metadata workbook | FAIL — same exact mismatch | NOT ACTIVATED |

No candidate row-bearing ZIP was downloaded to resolve the mismatch. The previous bounded Range probe for the all-program and Puglia ZIPs also remains failed. ProcRun does not use download-then-filter or download-then-inspect as a privacy qualification mechanism.

Because **zero new sources passed the mandatory schema-document gate**, no new source URL was added to `require_live_source()` and no collector expansion was performed. The requirement to run a full regression after each newly added source is therefore vacuously satisfied: there were no source additions in this round.

INTERREG and lower-priority candidates were not promoted after the higher-priority set failed the same mandatory exact comparison. This is not a claim that their underlying CSV transports differ; it is a statement that the public schema documentation available in this round does not prove equality with ProcRun's frozen 20-column runtime contract.

## Current live production boundary

Current live OpenCoesione route:

- `PR FESR Lombardia 2021-2027` only.

Before retrieval the live collector must pass `require_live_source("opencoesione_2021_2027_operations")`. It then requires exactly one CSV, UTF-8/UTF-8-BOM decoding, exact 20-column order, whole-batch rejection on schema/row failure, uniform list-update date, source URL and payload SHA-256. The two beneficiary identity columns are source-only and never enter `FundingProject`.

Customer and analytical claims must use this live runtime coverage, not the broader source-family universe. ProcRun must not describe funded-project coverage as all Italy or multi-region coverage while Lombardia is the sole activated programme.

## Formal conclusion

**A1 PUBLIC-EVIDENCE SOURCE-FAMILY QUALIFICATION: PASS for `OpenCoesione 2021-2027 EU cohesion operation-list ZIP/CSV` only.**

**Runtime activation: PASS for PR FESR Lombardia 2021-2027 only as of 2026-09-05.**

The all-program route and the six prioritised regional candidates are **NOT ACTIVATED** because the public 37.5 KiB metadata workbook does not satisfy exact equality with ProcRun's frozen 20-column transport contract. No human contact, permission request, source-owner clarification or row-bearing discovery fallback was used.

Portugal PRR and related Category-B routes remain permanently blocked. This decision does not alter the TED-scoped MVP OPEN contract.

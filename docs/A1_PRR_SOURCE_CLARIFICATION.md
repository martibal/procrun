# A1 — PRR Projects source-specific clarification

Status: **BLOCKING WEB BUILD / LIVE INGEST**

This document freezes the evidence that must be obtained before `prr_projects_dados_gov` can be
promoted from CONDITIONAL to APPROVED. General portal policy is supportive but is not sufficient for
ProcRun's absolute pre-receipt zero-natural-person rule.

## What public evidence establishes

As reviewed on 2026-09-03:

- dados.gov.pt generally permits open-data reuse and states that State datasets default to CC BY 4.0
  unless another licence is specified;
- dados.gov.pt states that datasets must not contain personal data, while its terms also recognise
  publication where consent or another legal basis permits personal information to be published;
- the PRR publisher exposes separate datasets for Projects, Entities, Locations and Public Contracts;
- the PRR Projects dataset page describes the dataset as project information, but its dataset-specific
  metadata currently shows `Licença não especificada`;
- the public dataset page does not itself freeze the exact production resource URL, response schema or a
  source-specific guarantee for the retained free-text project description.

These facts are not enough to prove that the exact machine response ProcRun would receive can never
contain a natural-person identifier.

## Exact approval questions

An authoritative response from the dataset publisher / dados.gov.pt operator must answer all of the
following for the exact PRR Projects production resource:

1. What is the canonical machine-readable URL/API route that should be used for automated recurring
   retrieval of the PRR Projects dataset?
2. What is the complete schema of that exact response, and can the response be restricted server-side
   to the ProcRun allowlist before any bytes are returned?
3. Can any field in that Projects response contain the name, email, telephone number, address, tax
   identifier or other identifier of a natural person?
4. Specifically, is the project title/description/scope free text subject to a publication control that
   guarantees that natural-person identifiers cannot be published in that field?
5. Is that guarantee enforced before publication/output, rather than being an instruction to data
   submitters or an expectation that consumers remove personal data after download?
6. What licence applies specifically to the PRR Projects resource where the portal currently displays
   `Licença não especificada`? Does it permit commercial reuse and transformation by a paid service,
   subject to attribution?
7. Is automated recurring retrieval of that exact resource permitted, and are there rate limits or
   other operational conditions that ProcRun must obey?
8. How are schema/resource changes communicated, and is there a stable version/schema identifier that
   can be checked so a changed route fails closed?

## Exact field surface requested

ProcRun needs only project-level fields. The requested production allowlist is:

- operation/project code;
- project title;
- project description/scope;
- project start date;
- project end date;
- approved funding amount;
- executed funding amount where available;
- fund/programme/objective/theme;
- region/municipality/NUTS where available;
- publication/first-seen timestamp where source-backed;
- canonical project source URL.

No beneficiary/entity/contact/person field is requested or permitted.

## Approval rule

A1 may become green only when the response is authoritative and unambiguous on all four independent
properties:

- **RIGHTS:** commercial reuse/derivative use of the exact Projects resource is allowed;
- **ACCESS:** recurring automated access to the exact route is allowed;
- **TRANSPORT:** only the approved field surface can reach the intelligence plane before receipt, or the
  exact Projects response is itself authoritatively guaranteed to contain no natural-person data;
- **FREE TEXT:** every retained text field is covered by the same pre-publication guarantee.

Any answer that merely says "personal data should not be entered", "the portal is open data", or
"consumers should remove personal data" is insufficient. `Download then filter` remains prohibited.

Until all four properties are green, the source contract remains CONDITIONAL and no collector may call
it from the intelligence plane.

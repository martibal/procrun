# ProcRun — OpenCUP structured-classification source qualification

Status date: 2026-09-11
Decision: **REJECTED FOR PRODUCTION INGESTION UNDER CURRENT RULES**
Phase: R / Task B

## Candidate value

OpenCUP publicly exposes project classification fields including project nature/type, intervention area, sector, subsector and category. These fields are relevant to ProcRun because they are structured, controlled-vocabulary metadata attached to the CUP project itself.

## Public evidence reviewed

Official DIPE/OpenCUP documentation establishes that:

- the CUP information set includes nature/type and intervention sector classification;
- OpenCUP publishes the CUP information asset publicly and updates it monthly;
- individual public project pages visibly expose classification fields such as Settore, Sottosettore and Categoria;
- the official OpenCUP API is REST/JSON and can be queried by CUP, **but API interoperability requires registration through the contact form**.

No human or source-owner contact was made.

## RIGHTS

**UNRESOLVED / not sufficient to approve production ingestion.**

The portal clearly makes data publicly viewable and describes it as open, but the reviewed API documentation did not provide a sufficiently precise machine-reuse licence/contract for ProcRun to treat the API route as independently approved. This gate does not need further investigation because ACCESS and DATA SAFETY already fail below.

## ACCESS

**FAIL.**

The official API documentation states that registration for interoperability services is requested through the `contattaci` form. ProcRun permanently prohibits requesting registration, permission, clarification or access from a human/source owner. Therefore the API route cannot be activated.

## DATA SAFETY

**FAIL.**

The public CUP project representation exposes the desired structured classification together with broader project/holder information, including holder denomination and CF/Partita IVA on public project pages. The reviewed official material does not document a server-side field projection that returns only Settore/Sottosettore/Categoria (and exact project identity needed for linkage) before ProcRun receives the response.

ProcRun therefore cannot retrieve the broad project payload and discard the unwanted identity-bearing fields afterwards. That would be the explicitly prohibited download-then-filter pattern.

## Production decision

The OpenCUP/Sistema CUP classification candidate is **rejected** for ProcRun production ingestion under the current source contract:

- RIGHTS: unresolved;
- ACCESS: fail because API registration requires contact;
- DATA SAFETY: fail because no documented pre-receipt field projection was established for the required classification-only payload.

No live API request, row probe or data download is permitted to try to work around those failures.

Task B is therefore closed per the Phase R specification and does not block Tasks A, C or D.

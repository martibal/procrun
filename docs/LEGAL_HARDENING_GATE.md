# ProcRun legal hardening gate

Status: **MANDATORY BEFORE COMMERCIAL ACTIVATION; GUI DESIGN MAY PROCEED ONLY AGAINST THIS CONTRACT.**

This gate freezes the legal/compliance boundary for the visual product. It does not replace applicable law or source terms. It makes the software fail closed where legal prerequisites are not yet satisfied.

## 1. Business-only service

ProcRun is designed for businesses and persons acting in a professional or commercial capacity. Consumer checkout is not supported. Any future checkout must collect a business identity assertion before purchase and must not present ProcRun as a consumer subscription.

## 2. Intelligence plane

The intelligence plane may contain only data admitted by an approved source contract. It must not ingest natural-person identity/contact fields. A source whose privacy safety depends on downloading a broad identity-bearing payload and filtering it afterwards is blocked.

The OpenCoesione 2021-2027 beneficiary/operation publication is admitted only because OpenCoesione's public catalogue states that the published beneficiary-name field for this publication contains legal persons only. Beneficiary name and beneficiary tax identifier remain source-only fields and are prohibited from persistence in `FundingProject`, the customer read model, exports and browser/API payloads. A change in that official publication contract invalidates the source approval.

## 3. Source reuse and verbatim text

Every production source must have a current public reuse basis. Verbatim source wording may reach a paid/customer surface only when the source contract or the exact Readiness source document is explicitly permitted for commercial republication.

For Readiness source packages:

- `COMMERCIAL_REUSE_CONFIRMED`: source wording may be rendered with attribution required by the source.
- `FACT_EXTRACTION_ONLY`: only structured facts, citations and official links may be rendered; `source_text` must be empty.
- `BLOCKED`: no production use.

Regione Lombardia website content is not presumed reusable. Its general legal notice restricts commercial reuse absent a specific licence or written authorisation. ProcRun never seeks individual permission; therefore an exact Lombardia document without an independently public commercial-reuse basis must remain `FACT_EXTRACTION_ONLY` if structured-fact use is independently supportable, otherwise `BLOCKED`.

## 4. Attribution

Customer surfaces that display or derive from approved source material must expose the applicable attribution. Current approved bases include:

- TED: procurement notices are reusable for commercial/non-commercial purposes unless otherwise stated; editorial content is CC BY 4.0. ProcRun must credit TED / Publications Office of the European Union, indicate transformations where applicable and never imply EU endorsement or use protected logos without permission.
- OpenCoesione: the approved 2021-2027 operation-list publication is CC BY 4.0. ProcRun must credit OpenCoesione / MEF-RGS-IGRUE and identify ProcRun analysis as derived.

## 5. Privacy/control plane

The zero-PII rule applies to the intelligence plane. A future customer control plane may process only the personal data necessary for authentication, security, billing, invoicing, support and legal compliance. Before such processing is activated, the Privacy notice must name the controller, purposes, legal bases, processors/recipients, retention, transfer safeguards where relevant, data-subject rights and complaint route.

No optional analytics, advertising or behavioural tracking may be enabled without a separate cookie/tracking compliance decision. Strictly necessary cookies only is the default launch posture.

## 6. Commercial terms and merchant disclosure

Checkout remains disabled until the site publishes the actual merchant identity and all legally required business information, including registered name, geographic address, electronic contact route, relevant register and organisation number, and VAT status where applicable.

Commercial terms must define at least service scope, B2B eligibility, price/VAT, billing period, renewal, cancellation, access suspension, IP/licence to outputs, acceptable use, source/upstream dependency, warranty limitations, liability allocation, governing law and venue.

## 7. Marketing truthfulness

A feature may not be advertised as included unless it exists in the production customer surface. Source wording must never be promised universally: wording is displayed only where the applicable reuse contract permits republication. Derived states must retain their evidence boundary; in particular OPEN remains TED-bounded.

## 8. Design/launch split

GUI design is authorised once this gate and its regression tests are green because design can use fixtures and frozen contracts. Commercial activation remains independently blocked until merchant/control-plane disclosures are complete and the exact Readiness bando source-package/snapshot combination has a `RELEASED` validation record.

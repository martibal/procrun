# ProcRun — source rights, access and third-party compliance

Status date: **2026-09-05**
Engineering review due: **2026-11-30**

This is an engineering compliance control, not a legal opinion. Approved source/provider reviews expire and are rechecked from public documentation only. No human response, source-owner contact, consultant opinion or external legal opinion is an allowed gate-closing mechanism.

## Approval model

A live intelligence source must pass all three gates:

1. **RIGHTS** — required commercial/value-added reuse is permitted.
2. **ACCESS** — the exact automated route is publicly permitted/available under its frozen conditions.
3. **DATA SAFETY** — prohibited natural-person data cannot enter the intelligence environment under the approved transport contract.

`CONDITIONAL` or `BLOCKED` at any required source gate prohibits production retrieval. Executable source contracts live in `src/procrun/source_contracts.py`.

ProcRun's intelligence plane has an absolute rule: **no natural-person data may enter the intelligence pipeline, database, model context, application logs or customer intelligence output.** Broad receipt followed by filtering is prohibited.

## Production source decisions

| Source / route | Overall | Production decision |
| --- | --- | --- |
| TED Search API projected route | APPROVED / LIVE | Field-projected procurement evidence and TED-scoped negative-search coverage |
| OpenCoesione 2021-2027 operation-list, exact approved route family | APPROVED / LIVE | Funded-project source; current live route PR FESR Lombardia |
| Broad OpenCoesione API / Projects / Soggetti | BLOCKED | Outside approved bounded contract |
| Mais Transparência project surfaces | BLOCKED | Do not ingest |
| PT2030 bulk workbook | BLOCKED | Broad identity-bearing transport; no download-then-filter |
| Portal BASE / APIBase2 current route | BLOCKED | No approved pre-receipt projection |
| Reviewed Poland public EU-funds project surfaces | REJECTED | No approved exact safe machine route |

## TED obligations

Official references are frozen in the executable/source qualification records. Production uses the Search API rather than CMS scraping, requests only the approved projected fields, excludes contact/supplier identity before receipt, observes the internal fair-use ceiling, preserves source meaning and does not imply EU endorsement.

Frozen customer attribution:

> Source: Tenders Electronic Daily (TED), Publications Office of the European Union. ProcRun transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement.

For MVP `OPEN` means exactly:

> **No relevant procurement found in TED as of DATE.**

## OpenCoesione obligations

The exact approved 2021-2027 EU-cohesion operation-list publication family is used under CC BY 4.0. The current production route is PR FESR Lombardia. The RGS publication instruction for project title/summary and the legal-person beneficiary rule form part of the frozen source contract; they are publication/provider rules, not claimed database-level impossibility guarantees. Any observed contract/schema violation fails the batch closed.

Beneficiary tax code/name are source-only fields and never enter canonical/customer-safe intelligence objects.

Frozen customer attribution:

> Source: OpenCoesione, Lista beneficiari e operazioni 2021-2027, used under CC BY 4.0. ProcRun transforms and classifies the source data; the derived analysis is not an official OpenCoesione, Italian-government or EU publication or endorsement.

## External services

The executable registry is `src/procrun/compliance.py`.

- **GitHub:** approved for source repository and CI. No production intelligence payload, customer data or secrets are committed.
- **Hetzner Cloud:** approved for the dedicated production intelligence runtime and backups under the frozen service contract.
- **Hugging Face:** approved only for the pinned benchmark-model download; hosted inference with project/customer data is not approved. The model is not required by the production MVP.
- **Stripe:** conditional future customer-control-plane service. It is deliberately a **web-phase** concern, not a pre-web blocker. Production activation requires the actual account/business to be accepted, then-current terms/restricted-business rules checked from public/account-visible material, payment/customer identity isolated from the intelligence plane, and the actual subscription/VAT/privacy flow implemented and tested.
- **Cloudflare:** optional/conditional; not part of the accepted non-web architecture. If introduced during web deployment, its exact features/privacy/logging impact must be reviewed before production activation.

## Software licences

See `THIRD_PARTY_NOTICES.md` and `src/procrun/compliance.py`. Runtime dependencies are exact-version pinned in `requirements-runtime.lock`; CI fails closed when required reviews expire. Current deployment is server-side SaaS. Any future on-prem/container distribution requires a new distribution-licence/SBOM review.

## Intelligence plane versus customer control plane

The non-web intelligence plane is production-accepted. Its customer-safe boundary is `src/procrun/read_model.py` (`customer-runway-v1`). Browser/API code may not read raw source payloads, beneficiary identity, buyer/contact identity, unvalidated candidates, model prompts or the internal ledger directly.

The customer website creates a separate control plane. The following are mandatory **web-phase launch controls**, not prerequisites for starting web development:

1. legal/merchant identity presentation appropriate to the actual seller;
2. customer Terms/subscription terms and Privacy Notice;
3. processor/subprocessor inventory for providers actually selected by the web implementation, with applicable provider DPAs/terms recorded from available documentation/account controls;
4. Stripe/payment activation if Stripe is used, including subscription/refund/VAT/invoicing behavior;
5. rendered source attribution/methodology and exact TED coverage wording;
6. no analytics, session replay or advertising SDK by default;
7. essential authentication/session cookies only unless a later explicit consent design approves more;
8. logging configured so customer network/account data does not enter the intelligence data plane;
9. customer/account/payment data stored separately from the immutable procurement intelligence ledger and never supplied to a model;
10. TLS, secret management, least privilege, customer-control-plane backup/recovery where applicable and documented incident/failure behavior;
11. final authentication/authorization, checkout/access, security-header, privacy and rendered-content validation before paid public launch.

No item above requires or permits source-owner/authority/customer outreach as a qualification mechanism. If an external service cannot be approved without a human response specifically obtained to close a ProcRun qualification gate, ProcRun does not use that service/path.

## Change control

A source/provider/model/dependency may not be silently promoted. Any change introducing a new intelligence source/service or changing a reviewed route must update the executable registry where applicable, retain current public terms/licence references, document commercial reuse/access/data-safety, record attribution and review dates, and preserve fail-closed regression coverage.

The current engineering review is due 2026-11-30. CI is intentionally allowed to fail after an applicable review expires until it is deliberately renewed from independently inspectable evidence.

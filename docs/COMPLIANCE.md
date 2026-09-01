# Procurement Runway — source rights, access and third-party compliance

Status date: **2026-09-01**  
Engineering review due: **2026-11-30**

This document records the compliance assumptions that are permitted to influence production code. It is an engineering control, not a legal opinion. Source and provider terms can change independently of the repository; approved reviews therefore expire and must be rechecked.

## 1. Approval model

A public source is not production-usable merely because it can be opened in a browser or downloaded without authentication. Procurement Runway separates three gates:

1. **RIGHTS** — commercial reuse and the required derivative/value-added use are permitted.
2. **ACCESS** — automated access is permitted through the exact route used, including rate, registration and authorization requirements.
3. **DATA SAFETY** — the response can be constrained before receipt so prohibited person/supplier fields never enter the intelligence environment.

A source may be `APPROVED` only when all three gates are `APPROVED`. `CONDITIONAL` or `BLOCKED` at any required gate prohibits live production retrieval. The executable registry is `src/procrun/source_contracts.py`.

The product has a stricter data-safety rule than many source terms require: **no natural-person data may enter the intelligence pipeline, database, model context, application logs or customer intelligence output.** A route that is lawful to access can still be blocked by ProcRun.

## 2. Current source decisions

| Source / route | Rights | Access | Data safety | Overall | Production decision |
| --- | --- | --- | --- | --- | --- |
| TED Search API | APPROVED | APPROVED | APPROVED | APPROVED | Live field-projected procurement source |
| Mais Transparência project search HTML | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | Human discovery/reference only; do not scrape as production feed |
| Mais Transparência project detail HTML | CONDITIONAL | CONDITIONAL | BLOCKED | BLOCKED | Do not ingest |
| PT2030 operations bulk workbook on dados.gov.pt | CONDITIONAL | APPROVED | BLOCKED | BLOCKED | Do not download into intelligence environment |
| Portal BASE / IMPIC APIBase2 | CONDITIONAL | CONDITIONAL | BLOCKED | BLOCKED | Do not call in production |

### 2.1 TED Search API

Official references:

- https://docs.ted.europa.eu/api/latest/search.html
- https://ted.europa.eu/en/legal-notice
- https://ted.europa.eu/en/news/fair-usage-policy-on-ted
- https://eur-lex.europa.eu/eli/dec/2011/833/oj

The Search API is explicitly provided for published-notice analysis/reuse and its documentation identifies commercial organisations integrating TED data into value-added platforms as intended users. TED's legal notice states that procurement notices in the Supplement to the Official Journal can be freely reused for commercial or non-commercial purposes unless otherwise noted.

Commission Decision 2011/833/EU permits commercial/non-commercial reuse and allows conditions such as source acknowledgement, preservation of original meaning and Commission non-liability.

ProcRun obligations:

- use the public Search API rather than automated scraping of TED CMS pages;
- request only the frozen projected field list in `collectors/ted.py`;
- exclude contact-person, email, phone, supplier/winner and other prohibited fields before receipt;
- stay below the published fair-use ceiling. TED currently states 700 HTTP requests in the last minute; ProcRun freezes an internal maximum of 600 requests/minute and should normally operate far below it;
- acknowledge TED/EU as source on customer-facing methodology/source surfaces;
- identify that Procurement Runway transforms/classifies the source data;
- do not imply EU endorsement;
- do not distort the original source meaning;
- do not rely on reuse rights for identifiable-person/third-party material outside the approved projection.

Frozen future public attribution:

> Source: Tenders Electronic Daily (TED), Publications Office of the European Union. Procurement Runway transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement.

### 2.2 dados.gov.pt and PT2030 operations

Official references:

- https://dados.gov.pt/pt/termos-de-utilizacao
- https://dados.gov.pt/fr/datasets/datasets-pt2030-03-lista-de-operacoes-pt2030/

The portal terms state that data uploaded by State bodies is published under CC BY 4.0 by default unless otherwise specified. The current PT2030 operations dataset page, however, displays **"Licença não especificada"**.

ProcRun therefore does **not** turn this specific dataset into unconditional `RIGHTS=APPROVED` merely by applying the portal-wide default. Before commercial reliance on that dataset, the source-specific licence basis must be clarified and frozen.

Independently of rights, the current resource is a broad workbook whose field surface can include beneficiary/entity/tax information. Under the pre-receipt zero-PII policy, download-then-filter is prohibited. This route is therefore `DATA SAFETY=BLOCKED` and may not be downloaded into the intelligence environment.

If a future field-bounded official route is approved under CC BY 4.0, customer-facing attribution must identify the source, link the applicable licence, and state that Procurement Runway has transformed/derived the data.

### 2.3 Mais Transparência

Official reference:

- https://transparencia.gov.pt/termos-e-condicoes

The portal terms state that portal contents are owned by ARTE or included with permission from the relevant rights holders, and the terms can change at any time. The portal is valuable as a human reference, but it does not provide the same clear production reuse contract as an approved underlying open-data/API route.

Production rule:

- do not build the commercial ingestion path by scraping portal HTML;
- do not archive full pages;
- use the portal only for manual research until a separately approved, field-bounded official transport is established.

The full project-detail route is additionally blocked because beneficiary content appears in the same response.

### 2.4 Portal BASE / IMPIC

Official references:

- https://www.base.gov.pt/Base4/pt/o-portal/base/
- https://www.base.gov.pt/Base4/pt/documentacao/formas-de-obter-dados-sobre-os-contratos-publicos/
- https://www.base.gov.pt/APIBase2
- https://www.base.gov.pt/Base4/pt/noticias/2025/api-para-consulta-de-dados-do-portal-base/
- https://www.base.gov.pt/Base4/media/aezdh4bi/portaria-318-b_2023_portal-base.pdf

Portaria 318-B/2023 states that public BASE data may be automatically extracted free of charge in open formats. Large-volume API extraction is conditional on registration and prior IMPIC authorization. BASE documentation says the API returns the same fields as the dados.gov files.

The documented API response includes `adjudicatarios` with identifiers/names, and the API does not document server-side output projection. BASE also warns that some published contract documents have contained personal data that should have been removed.

Current decision:

- APIBase2 remains `DATA SAFETY=BLOCKED`;
- no API call is permitted merely because an IMPIC token/authorization becomes available;
- any future IMPIC authorization terms must be retained and reviewed for the commercial use case;
- a future BASE route can be reconsidered only if prohibited fields can be excluded **before receipt**.

## 3. Evidence/attribution handling

Every production source contract must retain:

- exact retrieval route;
- legal/terms reference URLs;
- rights/access/data-safety statuses;
- terms review date and review-due date;
- attribution requirement/text where applicable;
- operational obligations such as rate limits, authorization and no-scraping requirements.

`require_live_source()` enforces this before a live collector runs. Approved source reviews fail closed after their due date.

Customer-facing outputs must expose source/provenance links and the bounded coverage statement. `OPEN` must never be worded as proof that procurement does not exist.

## 4. External service contracts

The executable registry is `src/procrun/compliance.py`.

### GitHub — APPROVED for development/CI

Terms: https://docs.github.com/en/site-policy/github-terms/github-terms-of-service

Allowed role: private source repository and CI/test execution. Production intelligence payloads, customer data, secrets and model weights must not be committed. Exact production data remains on the EU-hosted system.

### Hetzner Cloud — APPROVED for normal hosting/benchmarking

Terms: https://www.hetzner.com/legal/terms-and-conditions/

Allowed role: EU VPS hosting and ephemeral benchmark hosts. Normal commercial hosting only; prohibited activities such as cryptomining, abusive scanning or attack traffic are outside the product. Independent/offsite backup remains mandatory. Benchmark provisioning fails closed when the provider review expires.

### Hugging Face — APPROVED only for pinned model download

Terms: https://huggingface.co/terms-of-service

Allowed role: download the exact public Qwen GGUF artifact pinned in `model_registry.py`. Hosted Hugging Face inference with project/customer data is not approved. Arbitrary model downloads require a new licence/model-registry review. Model bytes are checked by exact size and SHA-256 before inference.

### Stripe — CONDITIONAL / future control plane

Terms: https://stripe.com/legal/ssa/no

Stripe is not part of the current intelligence pipeline. Activation is prohibited until the actual business/account is accepted, then-current prohibited/restricted-business rules are checked, VAT/payment/refund/subscription flows are designed for the actual legal entity, privacy/data-processing review is complete, and payment/customer identity is kept outside the intelligence ledger/model context.

### Cloudflare — CONDITIONAL / optional

Terms: https://www.cloudflare.com/terms/

Cloudflare is not required by the locked architecture. If introduced later for DNS/CDN/DDoS, the exact plan/features and privacy/logging impact must be re-reviewed before activation.

## 5. Software/model licences

See `THIRD_PARTY_NOTICES.md` and `src/procrun/compliance.py`.

The service is currently server-side SaaS. No ProcRun proprietary source licence is granted by this repository.

Direct production Python dependencies are exact-version pinned. The production runtime dependency closure is frozen in `requirements-runtime.lock` so transitive package drift cannot silently change the reviewed software surface.

Important components include PostgreSQL (PostgreSQL License), Qwen3-4B-GGUF Q4_K_M (Apache-2.0; benchmark candidate only), llama.cpp (MIT), httpx/httpcore (BSD-3-Clause), Psycopg/Psycopg Binary (LGPL-3.0-only), Pydantic/Pydantic Core (MIT), AnyIO (MIT), certifi (MPL-2.0), h11 (MIT), idna (BSD-3-Clause), annotated-types (MIT), typing-inspection (MIT) and typing-extensions (PSF-2.0).

If the product is later distributed on-premise as software/containers rather than only operated as a hosted service, all distribution/copyleft/notice obligations must be reviewed again and a complete SBOM/licence bundle generated.

## 6. Website/customer control-plane launch gate

The future customer website creates a different data-protection surface from the zero-PII intelligence plane. Before paid launch, the control plane must have its own documented architecture and legal review.

Required pre-launch items:

1. legal entity/merchant identity and business contact details finalized;
2. customer Terms of Service / subscription terms;
3. Privacy Notice covering account, billing, support and unavoidable network processing;
4. processor/subprocessor inventory and appropriate DPAs where required;
5. Stripe/payment account approval and VAT/invoicing design;
6. source attribution/methodology page with then-current approved source notices;
7. no analytics, session replay or advertising SDK by default;
8. essential authentication/session cookies only unless a later consent design explicitly approves more;
9. application/reverse-proxy logging configured so client IP is not persisted in the ProcRun application data plane;
10. customer/account data stored separately from the immutable procurement intelligence ledger and never supplied to the local model;
11. TLS, secret management, least privilege, backups/restore test and documented incident path;
12. short external legal review of then-current Portuguese source rights/attribution and customer-facing terms before commercial release.

This launch gate cannot be bypassed by source approval. Data-source legality and customer-account compliance are separate concerns.

## 7. Review/change-control rules

A source/provider/model/dependency may not be silently promoted because it is convenient. Any change introducing a new external source/service or changing a reviewed route must include, as applicable: updated executable registry entry; current terms/licence URLs; explicit commercial-reuse and automated-access status; PII/field-surface audit; attribution obligation; review date/due date; and a regression test proving that an expired/non-approved entry fails closed.

The current review date is 2026-09-01 and review due date is 2026-11-30. CI is intentionally allowed to fail after that date until the relevant terms are rechecked and deliberately renewed.
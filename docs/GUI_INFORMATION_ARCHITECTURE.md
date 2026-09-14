# ProcRun GUI information architecture

Status: **FROZEN DESIGN CONTRACT BEFORE VISUAL IMPLEMENTATION**

## 1. One product, one mental model

ProcRun has two analytical tracks:

1. funded-project procurement intelligence;
2. Readiness Dossier.

They must not be presented as unrelated products. Their shared product principle is that three epistemic layers are always separated:

1. **Source fact** — what the approved public source actually establishes;
2. **ProcRun interpretation** — what ProcRun can deterministically derive inside the frozen rules;
3. **Professional review** — what ProcRun refuses to decide and leaves to the user/adviser.

The GUI must preserve this three-layer mental model in both tracks. Visual hierarchy, labels and interaction patterns should make the layer boundary immediately recognisable when the user moves between project intelligence and Readiness.

The design may use columns on wide screens, stacked labelled sections on narrow screens, or another responsive representation, but the semantic ordering must remain:

**Source fact → ProcRun interpretation → Professional review**.

No visual treatment may merge source evidence and ProcRun interpretation into one undifferentiated answer.

## 2. Sparse customer-facing navigation

A normal customer must be able to use ProcRun through no more than **three to four primary product surfaces**, including the customer's own saved/account area.

The target primary structure is:

1. **Home** — product understanding, trust, concise methodology explanation, pricing model and entry into the product;
2. **Explore** — funded projects, bandi/calls, filtering, project/call detail, source evidence and procurement assessment;
3. **Readiness** — structured project input, preview, pre-purchase disclosure, checkout and paid dossier workflow;
4. **My ProcRun** — purchased dossiers, saved opportunities/cases when implemented, account and customer storage features.

`Methodology` is the intentional supporting exception: it is a deep technical/reference surface, not a required step in the normal customer journey. `Terms` and `Privacy` are permanent legal/reference pages and are not primary product navigation.

No new primary page may be created when a function can naturally exist as a state, panel, drawer, tab or step inside an existing primary surface. Project detail, bando detail, checkout review, dossier view, saved opportunities and source detail should therefore remain inside the appropriate primary surface unless a separate route is technically required for persistence, sharing, accessibility or indexing.

The customer-facing mental journey should remain recognisable as:

**Home → Explore → Readiness → My ProcRun**

or, for returning/search-driven users:

**Explore → Readiness → My ProcRun**.

## 3. Methodology as semantic hub

`Methodology` is the canonical semantic centre of the product.

Every ProcRun-specific term used in the GUI must have:

- one canonical term;
- one short customer-facing definition;
- one stable methodology anchor;
- an explicit list of contexts in which the term may be used.

The GUI must not invent local definitions of ProcRun-specific terminology on individual pages/components.

Wherever a ProcRun-specific term appears and explanatory help is useful, the interaction pattern is:

**hover/focus/tap → concise explanation → “Read more” → exact Methodology anchor**.

Desktop hover must have an accessible keyboard/focus equivalent. Mobile must use tap/popover or another explicit interaction rather than relying on hover.

The short explanation must be sufficient for normal use without forcing the customer to leave the current workflow. `Read more` is for customers who want the deeper technical definition, source rules, calculation details, examples or limitations.

Methodology therefore operates as a hub-and-spoke semantic architecture:

- Home consumes canonical terms;
- Explore consumes canonical terms;
- Readiness consumes canonical terms;
- My ProcRun/dossiers consume canonical terms;
- future product modules may consume the same canonical terms without creating cross-page definition meshes.

A future product surface should connect to the semantic hub instead of requiring indirect explanatory links to every other product surface.

## 4. SEO architecture: indexed states, not page proliferation

Organic search is part of the information architecture, not a later marketing layer.

ProcRun must not respond to SEO needs by creating a large blog-like or page-per-feature navigation tree. Instead, the **Explore** product surface must support stable, crawlable, indexable routes for validated entities and high-intent search entry points.

Examples include:

- `/explore/<stable-bando-or-call-slug-or-id>`;
- `/explore/<stable-funded-project-slug-or-id>`.

A routed entity detail is an **indexed state of Explore**, not a new conceptual product page. A customer arriving directly from a search engine must still recognise that they are inside Explore and must be able to continue directly into Readiness when applicable.

The preferred organic journey is:

**Search engine → specific validated Explore entity → optional Methodology drill-down → Readiness → My ProcRun**.

SEO content should therefore be generated from validated structured product data and source-backed facts wherever possible, rather than from generic keyword articles written solely to attract traffic.

Each indexable Explore entity must be independently understandable when entered directly from search. At minimum it should expose, subject to source/reuse rules:

- canonical entity title and stable identifier;
- current state/freshness where applicable;
- who/what the programme or project concerns;
- key published structured facts;
- source attribution and official source access;
- ProcRun's bounded interpretation where available;
- clear explanation of what ProcRun can and cannot establish;
- relevant Readiness entry point when an exact validated call/bando supports it;
- contextual links to Methodology terms rather than duplicated local methodology prose.

SEO metadata and rendered copy must never outrun the validation state. A non-released or incomplete entity may be discoverable only to the extent permitted by the product/source contract and must not be described as commercially validated when it is not.

The architecture must preserve canonical URLs and avoid creating multiple crawlable routes that represent the same entity/state without a deliberate canonicalisation rule.

## 5. Funded-project procurement track

### Source fact

Show the admitted project evidence and procurement evidence with provenance where reuse rights permit republication.

### ProcRun interpretation

Component assessment uses the frozen domain state:

- `OPEN`
- `CLOSED`
- `UNRESOLVED`

Project assessment may additionally be `PARTIAL` where component-level states differ.

These labels answer a bounded procurement question about a component/project under ProcRun's accepted evidence universe. They are not raw TED-observation labels and they are not eligibility/readiness outcomes.

### Professional review

`UNRESOLVED` is not a generic failure state. The UI must expose the exact admitted source evidence that triggered or explains the unresolved condition, subject to source-reuse rights. Where verbatim republication is not allowed, show the permitted structured fact/citation/link and explain why the source wording is not reproduced.

## 6. Readiness track

Readiness intentionally does **not** reuse `OPEN/CLOSED/UNRESOLVED` for requirement outcomes.

### Source fact

Show the published requirement, exact mechanical boundary or structured requirement fact, citation and official source link. Verbatim wording is shown only for `COMMERCIAL_REUSE_CONFIRMED` documents.

### ProcRun interpretation

Mechanical comparisons use the frozen result codes:

- `BELOW_PUBLISHED_MINIMUM`
- `ABOVE_PUBLISHED_MAXIMUM`
- `WITHIN_PUBLISHED_BOUNDARY`
- `INPUT_NOT_SUPPLIED`

These are factual comparisons between a declared project input and an exact published boundary. They must never be restyled or renamed so they appear to be eligibility verdicts.

### Professional review

Context-dependent requirements use adviser/professional states:

- `CONFIRMED_BY_ADVISOR`
- `NOT_CONFIRMED`
- `PROFESSIONAL_REVIEW_REQUIRED`

The UI must treat professional review as a first-class outcome, not as an error, footnote or disabled-state afterthought.

## 7. Terminology rule across tracks

The vocabulary is intentionally different because the underlying questions are different.

- `OPEN/CLOSED/UNRESOLVED` = ProcRun's bounded component/project procurement assessment.
- Readiness mechanical result codes = direct comparison to published numerical boundaries.
- Readiness adviser/professional states = human/professional determination outside ProcRun's authority.

The GUI must not silently present these vocabularies as interchangeable.

Where a customer moves from a funded-project view into Readiness, the transition must contain a concise explanation such as:

> Procurement status and Readiness checks answer different questions. Procurement status describes what ProcRun found in the accepted procurement evidence. Readiness compares your project inputs with published requirements and leaves professional judgments to you or your adviser.

This explanatory boundary should be available at the transition point and through contextual help, rather than repeated as long disclaimer text on every row.

## 8. Source-text visibility rule

Source-text visibility is a rights-controlled product behaviour, not a formatting accident.

### `COMMERCIAL_REUSE_CONFIRMED`

The UI may show admitted verbatim source wording together with source attribution and provenance.

### `FACT_EXTRACTION_ONLY`

The UI must not show protected source wording. It must instead show:

- the permitted structured fact;
- the exact citation or document reference;
- the official source link;
- a short customer-facing explanation that wording is not reproduced because ProcRun is permitted to use the structured fact/reference but not commercially republish the source text.

Recommended compact copy:

> Source wording is not reproduced for this document. ProcRun shows the structured fact, citation and official source link under the applicable source-use terms.

### `BLOCKED`

The document must not appear in a production customer analysis.

The absence of a quote must therefore never look like missing data or an ingestion error when the reuse mode is `FACT_EXTRACTION_ONLY`.

## 9. Cross-track visual consistency

The shared design system must encode epistemic role rather than product module.

The same visual treatment should consistently identify:

- **Source fact** across both tracks;
- **ProcRun interpretation** across both tracks;
- **Professional review** across both tracks.

Colour alone must not carry this distinction. Labels, section headings, iconography/shape if used, ordering and accessible text must preserve the meaning.

Status colours for `OPEN/CLOSED/UNRESOLVED` must not be reused in a way that suggests equivalence with Readiness mechanical results or professional-review states.

## 10. Navigation and product continuity

The navigation must reinforce one workflow rather than two products:

1. discover and inspect a funded project or validated call/bando;
2. understand the source evidence and bounded procurement assessment;
3. where applicable, move into Readiness for a specific bando/call;
4. compare structured project inputs with published requirements and historical context;
5. identify what is mechanically established and what still requires professional review;
6. preserve purchased/saved work in My ProcRun where the product contract supports storage.

A Readiness entry point from a project or bando must therefore explain why it is relevant instead of behaving like navigation to a separate application.

## 11. Design acceptance criteria

A GUI design is not acceptable unless all of the following are true:

- a normal customer journey uses no more than three to four primary product surfaces including the customer account/storage area;
- Methodology is the canonical semantic hub for ProcRun-specific terminology;
- contextual help provides a concise definition and a direct `Read more` path to the correct Methodology anchor;
- no product surface maintains a conflicting local definition of a canonical ProcRun term;
- indexed SEO routes are represented as states of Explore rather than new conceptual product sections;
- a search-engine visitor can land directly on an indexed Explore entity and understand it without visiting Home first;
- validated structured product data is preferred over generic SEO-article proliferation;
- canonical URL handling prevents accidental duplicate indexed representations of the same entity;
- a user can distinguish source fact from ProcRun interpretation without opening methodology documentation;
- professional-review items are visually first-class and cannot be mistaken for system errors;
- `OPEN/CLOSED/UNRESOLVED` is never used as a Readiness eligibility vocabulary;
- Readiness result codes are never presented as procurement states;
- the transition between the two tracks explains why their status vocabularies differ;
- verbatim source text is controlled by reuse mode;
- `FACT_EXTRACTION_ONLY` produces an explicit rights-based explanation instead of a blank/missing quote;
- the same three epistemic layers remain recognisable on desktop and mobile;
- responsive layout may change geometry but not semantic ordering;
- visual polish must not weaken any frozen backend, legal or source-reuse boundary.

This document is a design contract. Visual implementation may refine typography, spacing, density, hierarchy and responsive composition, but may not change these semantics without first changing the underlying product contract.

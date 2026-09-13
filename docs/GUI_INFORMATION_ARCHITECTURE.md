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

## 2. Funded-project procurement track

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

## 3. Readiness track

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

## 4. Terminology rule across tracks

The vocabulary is intentionally different because the underlying questions are different.

- `OPEN/CLOSED/UNRESOLVED` = ProcRun's bounded component/project procurement assessment.
- Readiness mechanical result codes = direct comparison to published numerical boundaries.
- Readiness adviser/professional states = human/professional determination outside ProcRun's authority.

The GUI must not silently present these vocabularies as interchangeable.

Where a customer moves from a funded-project view into Readiness, the transition must contain a concise explanation such as:

> Procurement status and Readiness checks answer different questions. Procurement status describes what ProcRun found in the accepted procurement evidence. Readiness compares your project inputs with published requirements and leaves professional judgments to you or your adviser.

This explanatory boundary should be available at the transition point and through contextual help, rather than repeated as long disclaimer text on every row.

## 5. Source-text visibility rule

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

## 6. Cross-track visual consistency

The shared design system must encode epistemic role rather than product module.

The same visual treatment should consistently identify:

- **Source fact** across both tracks;
- **ProcRun interpretation** across both tracks;
- **Professional review** across both tracks.

Colour alone must not carry this distinction. Labels, section headings, iconography/shape if used, ordering and accessible text must preserve the meaning.

Status colours for `OPEN/CLOSED/UNRESOLVED` must not be reused in a way that suggests equivalence with Readiness mechanical results or professional-review states.

## 7. Navigation and product continuity

The navigation must reinforce one workflow rather than two products:

1. discover and inspect a funded project;
2. understand the source evidence and bounded procurement assessment;
3. where applicable, move into Readiness for a specific bando/call;
4. compare structured project inputs with published requirements and historical context;
5. identify what is mechanically established and what still requires professional review.

A Readiness entry point from a project must therefore explain why it is relevant to that project/call instead of behaving like navigation to a separate application.

## 8. Design acceptance criteria

A GUI design is not acceptable unless all of the following are true:

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
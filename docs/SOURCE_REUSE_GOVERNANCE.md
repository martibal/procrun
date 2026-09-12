# ProcRun public-source reuse governance — permanent invariant

## Absolute rule

ProcRun must never depend on an individual permission, legal opinion, source-owner response, registration approval, contact-form reply, negotiated licence, or any other human/external approval before a production source can be used.

Every production source must be justified exclusively by publicly inspectable material: legislation, regulations, official licence/terms pages, official source metadata, or other independently verifiable public documentation.

If the required commercial use cannot be justified from public material, ProcRun must either restrict itself to facts/metadata that can be used without republishing protected expression, or reject the source. Contacting a person to obtain permission is never a fallback path.

## Required source-reuse states

Every document entering a paid Readiness source package must declare exactly one reuse state:

- `COMMERCIAL_REUSE_CONFIRMED` — public legislation/licence/terms explicitly supports the intended commercial reuse. The public basis must be recorded.
- `FACT_EXTRACTION_ONLY` — the document is publicly available and may support structured facts, boundaries, citations and links, but ProcRun has no sufficiently documented public basis to commercially republish the source wording. Paid output must not reproduce the source text.
- `BLOCKED` — the intended use would require individual permission, human contact, registration/approval, a non-public legal interpretation, or another external approval. The document cannot enter a production source package.

## Enforcement

1. A `BLOCKED` document makes the source package invalid.
2. `COMMERCIAL_REUSE_CONFIRMED` requires a non-empty public reuse-basis URL and basis note.
3. `FACT_EXTRACTION_ONLY` also requires a public basis explaining the restriction and must not carry source wording into the paid source package; only structured facts, citation references and the official URL are permitted.
4. Source-package manifests and hashes bind the reuse state and public basis, so the legal-use assumption is immutable and auditable for every dossier.
5. A change in licence, terms or statutory basis requires a new source-package version; old packages are never silently rewritten.
6. Silence is never permission. Ambiguity fails closed to `FACT_EXTRACTION_ONLY` or `BLOCKED`.

## Relationship to the no-contact rule

This invariant extends the permanent no-human-contact rule at the top of `README.md`. A source is not eligible merely because it is public or technically accessible. The intended commercial use itself must be supportable from public, independently inspectable material.

The valid decision path is always:

**publicly documented right -> GO**

**publicly documented restriction -> build within the restriction**

**individual permission / external approval required -> NO-GO**

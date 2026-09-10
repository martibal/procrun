# Classification engine production validation gate

Status: **SUPERSEDED FOR PRODUCTION BY EVIDENCE-BOUNDED SEMANTICS**

The historical A21 programme defined an inferential engine target: independent human gold-standard adjudication, a stratified final holdout, fixed component precision/recall and state-accuracy thresholds, and zero false OPEN. The repository contains tooling and historical work for that programme, but the independent final gold standard was never completed. It is therefore prohibited to describe that historical gate as passed.

ProcRun production no longer depends on that inferential claim class. The live product uses the authoritative contract in `docs/EVIDENCE_BOUNDED_PRODUCTION_SEMANTICS.md`:

- components require exact frozen phrases in approved project source wording;
- no model/LLM fallback may create a production component;
- unresolved/unmatched project wording produces `UNRESOLVED` and remains visible;
- CLOSED requires exact accepted TED source evidence;
- plausible structural candidates that cannot establish CLOSED produce `UNRESOLVED`;
- OPEN is only the rule-bounded observation that no match satisfying the frozen exact-evidence rules was found in the complete TED universe through the cutoff;
- project aggregation is deterministic and fail-closed.

Because those claims are direct invariants over source text, structural facts, source completeness and deterministic code, the production release gate is the live `infrastructure-closure` proof rather than a self-referential classifier benchmark. The proof runs the complete approved source path, verifies exact spans and state invariants, runs the build three times for determinism, writes through the append-only PostgreSQL ledger and checks the customer-output hash.

This is not a relaxation of the old standard. It removes the unprovable semantic assertion from the product. Any future production feature that infers components beyond exact approved wording, broadens OPEN into a statement of real-world absence, or uses model-generated semantic classification must reopen a new independent external-gold validation gate before release.

Historical A21 artifacts and documents are retained as provenance unless explicitly archived. They are not launch blockers for the evidence-bounded production path and are not evidence that the historical inferential benchmark passed.

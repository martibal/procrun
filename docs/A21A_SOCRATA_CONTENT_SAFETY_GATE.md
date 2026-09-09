# A21a Lombardia Socrata content-safety gate

Status: **CONDITIONAL — PROJECTION PASS, CONTENT-SAFETY NOT PROVEN**

The Regione Lombardia PR FESR 2021-2027 Socrata dataset (`q78n-g3m9`) passed the structural projection gate: ProcRun can request only the frozen project-field allowlist and omit the dedicated beneficiary identity fields before the response is returned.

That is necessary but not sufficient for ProcRun's absolute zero-PII rule.

`descrizione_operazione` is free text. Public documentation establishes that it is the project description, but it does not establish that every value is guaranteed to contain no natural-person data. A server-side column projection cannot remove identity information that might be embedded inside an otherwise allowed free-text value.

Therefore:

- the source remains `CONDITIONAL` for A21a;
- bulk project-row retrieval is not approved;
- no `a21a-sanitized-source-pool-v1` package may be labelled `ZERO_PII_CONFIRMED` from this route yet;
- download-then-filter, receive-then-redact, local preprocessing, model-based PII cleanup and post-receipt screening are all prohibited as substitutes for a pre-receipt safety contract;
- the earlier one-row projection probe proved only field-level projection and must not be interpreted as a zero-PII content certification.

## What would close this gate

Only already-public evidence can close the gate. The evidence must establish a pre-receipt rule strong enough to guarantee that the allowed project-description surface cannot contain natural-person data, or provide a separate server-side source field whose contract itself guarantees such content safety.

If no such public contract exists, this source cannot provide A21a verbatim project evidence under the current absolute zero-PII requirement and must remain non-ingestible.

No human contact, exception request or legal clarification workflow is permitted.

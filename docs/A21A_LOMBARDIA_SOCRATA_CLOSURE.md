# A21a Lombardia Socrata content-safety closure

Status: **BLOCKED FOR A21a VERBATIM SOURCE EVIDENCE**

Regione Lombardia dataset `q78n-g3m9` passed the server-side projection gate: ProcRun can request only allowlisted project columns and exclude beneficiary identity columns before receipt. That property remains useful, but it is not sufficient for ProcRun's absolute zero-PII rule.

The remaining required field is `descrizione_operazione` (`Descrizione del progetto`). A public-documentation review found no dataset-specific contract stating that this free-text field is guaranteed to contain no natural-person data. Regione Lombardia's own Open Data governance is explicitly compatible with publication of datasets containing personal data after the data owner has assessed legality and necessity and assumed responsibility for publication. Therefore publication on the Open Data portal is not itself a zero-PII attestation.

EU Regulation 2021/1060 requires publication of information about funded operations and permits beneficiaries to include natural persons in scope. It does not establish a guarantee that an arbitrary operation-description free-text value is devoid of personal data.

Consequences for ProcRun:

- no bulk `descrizione_operazione` retrieval is permitted for A21a;
- no package derived from this free-text field may be attested `ZERO_PII_CONFIRMED` solely because the source is Open Data Lombardia;
- post-receipt regex, NER, redaction, or filtering cannot cure the boundary because download-then-filter is prohibited;
- the successful Socrata column-projection proof remains recorded, but the source candidate is `BLOCKED` for the evidence-text role;
- reopening requires a public, source-specific pre-receipt contract that guarantees the requested text field contains no natural-person data. External contact or ad-hoc assurances are not an allowed path.

No project rows were bulk downloaded as part of this decision, and the sealed A21 holdout remains untouched.

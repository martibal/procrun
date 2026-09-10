# A21a Lombardia Socrata row-receipt guard

Status: **METADATA-ONLY; PROJECT-ROW RECEIPT PROHIBITED**

Dataset: `https://www.dati.lombardia.it/resource/q78n-g3m9.json`

Regione Lombardia's Socrata surface is technically capable of server-side field projection. Public dataset metadata identifies `descrizione_operazione` as the project-description field and also confirms that the same dataset contains beneficiary identity fields, including beneficiaries that may be natural persons.

The transport capability is therefore not the blocker. The blocker is the content contract: no dataset-specific public rule has been established that guarantees `descrizione_operazione` cannot contain natural-person data before publication. Under ProcRun's zero-PII and upstream-before-receipt requirements, requesting even one projected project row would therefore be an impermissible experiment on an unqualified free-text field.

Accordingly:

- metadata inspection of the dataset schema remains allowed;
- no project row may be requested from the Socrata resource;
- `$select` capability alone is not sufficient to admit a field;
- no row value may be fetched merely to inspect, redact or empirically test it;
- this route may be reconsidered only if public source documentation establishes a pre-receipt zero-PII rule for the retained project text or proves exact field identity to another already-qualified field contract.

The probe `scripts/probe_a21a_lombardia_socrata_projection.py` is therefore metadata-only and fails closed before any row-bearing resource URL can be constructed.

This guard does not alter the separate RGS/OpenCoesione finding that `TITOLO_PROGETTO` and `SINTESI_PROG` are qualified fields in the bounded source contract. It only prevents that qualification from being transferred to the Socrata `descrizione_operazione` field without explicit public lineage evidence.

# A21a OpenCoesione `SINTESI_PROG` requalification

Status: **APPROVED AS A21a SOURCE-EVIDENCE INPUT UNDER THE EXISTING PR FESR LOMBARDIA SOURCE CONTRACT**

## Safety correction

A later A21a source review incorrectly recorded that the RGS/OpenCoesione rules explicitly protected `TITOLO_PROGETTO` from natural-person information but did not establish an equivalent rule for `SINTESI_PROG` / `SintesiProgetto_OperationSummary`.

That conclusion is wrong.

The primary source is:

`https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`

In **Vademecum Monitoraggio, versione 1.0, dicembre 2024, AP00 - Anagrafica progetto**, the document first defines `SINTESI_PROG` as a maximum-1,300-character summary describing what the project realizes, its purpose and, where necessary, territory. It then states explicitly:

> Nei campi TITOLO_PROGETTO e SINTESI_PROG non vanno inserite informazioni sensibili riferibili a persone fisiche, quali il nome, il Codice fiscale, il numero di telefono o l’indirizzo e-mail.

This is one rule covering both fields. ProcRun must therefore apply the same source-safety conclusion to both.

## Empirical live-source result

The remote A21a diagnostic subsequently evaluated the current logical PR FESR Lombardia universe: **4,305 projects**.

Observed result:

- source wording equal to project title: **4,305 / 4,305**;
- source wording distinct from project title: **0 / 4,305**;
- wording length at least 100 characters: **469 / 4,305**;
- wording length at least 200 characters: **37 / 4,305**.

This establishes that the current `SINTESI_PROG` surface does not provide a second, richer description layer beyond the project title in this live source.

## Product consequence

That finding does **not** invalidate the source for ProcRun 2.0.

For the current Lombardia source, the customer-facing evidence wording must be treated and labeled as **`Project title`**, not represented as a richer `Project description`. The exact title may still be valid and useful evidence when it is the source wording that explains why the project was selected as relevant.

A21a therefore validates usefulness and correctness of the **best available source wording**, rather than requiring a minimum document length or 1–3 full sentences. See `A21A_SOURCE_WORDING_SEMANTICS.md` and `A21A_EVIDENCE_RETRIEVAL_GATE.md`.

A richer approved description source may be added later, but finding one is not a prerequisite merely because the current source wording is title-length.

## Scope

This decision does not reopen:

- the general OpenCoesione project API;
- the OpenCoesione project-search CSV export;
- OpenBDAP MOP;
- Regione Lombardia Socrata.

The decision remains limited to the existing bounded PR FESR Lombardia operation-list contract and its approved project-text fields.

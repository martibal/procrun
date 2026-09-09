# A21a OpenCoesione `SINTESI_PROG` requalification

Status: **APPROVED AS A21a SOURCE-EVIDENCE TEXT UNDER THE EXISTING PR FESR LOMBARDIA SOURCE CONTRACT**

## Correction

A later A21a source review incorrectly recorded that the RGS/OpenCoesione rules explicitly protected `TITOLO_PROGETTO` from natural-person information but did not establish an equivalent rule for `SINTESI_PROG` / `SintesiProgetto_OperationSummary`.

That conclusion is wrong.

The primary source is:

`https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf`

In **Vademecum Monitoraggio, versione 1.0, dicembre 2024, AP00 - Anagrafica progetto**, the document first defines `SINTESI_PROG` as a maximum-1,300-character summary describing what the project realizes, its purpose and, where necessary, territory. It then states explicitly:

> Nei campi TITOLO_PROGETTO e SINTESI_PROG non vanno inserite informazioni sensibili riferibili a persone fisiche, quali il nome, il Codice fiscale, il numero di telefono o l’indirizzo e-mail.

This is one rule covering both fields. ProcRun must therefore apply the same source-safety conclusion to both.

## Consequence

`SintesiProgetto_OperationSummary` is eligible as the primary project-text surface for A21a evidence retrieval on the already-approved OpenCoesione **PR FESR Lombardia 2021-2027 operation-list** route.

This does not prove that the summary is useful enough for the customer-facing evidence layer or that the extractor reaches the required quality thresholds. Those are separate empirical gates and are the next validation task.

## Scope

This decision does not reopen:

- the general OpenCoesione project API;
- the OpenCoesione project-search CSV export;
- OpenBDAP MOP;
- Regione Lombardia Socrata.

The correction is limited to the existing bounded operation-list contract and the `SINTESI_PROG` field within that contract.

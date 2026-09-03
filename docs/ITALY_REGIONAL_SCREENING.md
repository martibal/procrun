# Italy regional 2021-2027 source screening

Status date: 2026-09-03.

This note records a metadata/documentation-only screening of five large Italian regional 2021-2027 programme publication routes after the national/OpenCoesione/Kohesio routes were rejected. It does not approve any new source and does not change `SOURCE_CONTRACTS`.

ProcRun's boundary remains unchanged: no project/beneficiary row body may be received unless the requested transport excludes prohibited personal-data fields before receipt and any free-text scope field used for component evidence has an adequate pre-publication zero-PII guarantee.

## Result

**No screened regional route qualifies for a project-row smoke test.**

| Region | Observed public route | Pre-receipt projection | Scope status | Other blocker | Decision |
| --- | --- | --- | --- | --- | --- |
| Emilia-Romagna | PR FESR 2021-2027 CSV/XLSX bulk publication under Article 49 | **NOT ESTABLISHED** | Article-49 project publication exists, but no separately field-safe scope artifact or zero-PII free-text guarantee was found | Bulk project/beneficiary publication | **REJECTED / NO ROW TEST** |
| Piemonte | PR FESR 2021-2027 Excel/CSV publication; regional page also points to OpenCoesione | **NOT ESTABLISHED** | No independent field-safe project-scope route was found | Duplicates an already rejected OpenCoesione family for richer navigation | **REJECTED / NO ROW TEST** |
| Toscana | PR FESR 2021-2027 operation list published as XLSX/CSV under Article 49 | **NOT ESTABLISHED** | No documented source-side projection or zero-PII guarantee for project scope was found | Static bulk distribution | **REJECTED / NO ROW TEST** |
| Veneto | Official FESR page directs users to OpenCoesione for the complete beneficiary/project list | **N/A as independent route** | No materially independent project-data transport identified | Falls back to already rejected OpenCoesione route | **REJECTED AS DUPLICATE ROUTE** |
| Sicilia | PR FESR Sicilia 2021-2027 operation list on EuroInfoSicilia CKAN/XLSX publication | **NOT ESTABLISHED** | No field-safe scope transport established | Current CKAN dataset page labels the licence `Other (Non-Commercial)` | **REJECTED — RIGHTS FAIL** |

## Evidence reviewed

### Emilia-Romagna

Official PR FESR pages publish the selected/financed 2021-2027 projects as CSV and Excel and state that the list is published under Article 49 of Regulation (EU) 2021/1060. Current pages expose bulk files, including multi-megabyte CSV/XLSX distributions.

References:
- https://fesr.regione.emilia-romagna.it/progetti-attivita/progetti-finanziati/progetti-21-27
- https://fesr.regione.emilia-romagna.it/progetti-attivita/progetti-finanziati/progetti-21-27/dati-in-formato-aperto/2025-12-31/20251231-dati-comunicazione-fesr.csv

No authoritative server-side output-column projection contract or separately published field-safe project-scope artifact was found during this screening. Because receiving a bulk file and discarding beneficiary/identity fields afterwards is prohibited, no file body was fetched.

### Piemonte

The official regional page provides an updated PR FESR 2021-2027 beneficiary/operation list in Excel and CSV. It also explicitly says the same data are provided through OpenCoesione and links to the OpenCoesione beneficiary/operation route.

Reference:
- https://www.regione.piemonte.it/web/temi/fondi-progetti-europei/fondo-europeo-sviluppo-regionale-fesr/monitoraggio-valutazioni/operazioni-beneficiari-dati-aggiornati-sullattuazione-pr-fesr-2021-2027

No independent pre-receipt field projection or separately field-safe project-scope distribution was found. The OpenCoesione path has already been rejected under the same zero-PII boundary, so it is not reopened here. No project/beneficiary file body was fetched.

### Toscana

The official PR FESR 2021-2027 page publishes the operation list as XLSX and CSV and states that it is maintained under Article 49 of Regulation (EU) 2021/1060.

Reference:
- https://www.regione.toscana.it/-/pr-fesr-2021-2027-elenco-dei-beneficiari

The screening found no documented output-field projection for these static distributions and no separate source-side-safe scope artifact. No operation file body was fetched.

### Veneto

The official Veneto Coesione page states that the Article-49 selected-operation list is available and directs users to OpenCoesione for statistics, project information and the complete beneficiary list.

Reference:
- https://venetocoesione.regione.veneto.it/fesr/operazioni-selezionate-e-operazioni-di-importanza-strategica

This does not establish a materially independent field-bounded regional transport. The previously rejected OpenCoesione route therefore remains outcome-determinative. No project body was fetched.

### Sicilia

EuroInfoSicilia exposes current PR FESR Sicilia 2021-2027 operation-list datasets through its CKAN catalogue, with XLSX resources. The current dataset page for the 22 January 2026 operation list labels the licence as **Other (Non-Commercial)**.

References:
- https://opendata.euroinfosicilia.it/en/dataset/elenco-operazioni-del-pr-fesr-sicilia-2021-2027-aggiornato-al-22-gennaio-2026
- https://opendata.euroinfosicilia.it/it/dataset/

That licence is independently incompatible with ProcRun's intended commercial product use, so the route fails before any data-safety or row-level test. No XLSX/CSV body was fetched.

## Consolidated gate

The five-region screen does not produce a candidate satisfying both of ProcRun's hard requirements:

1. project-specific scope rich enough for exact component evidence spans; and
2. a source-side/pre-receipt guarantee that ProcRun can receive that scope without receiving personal data.

The regional search also demonstrates that merely finding another Article-49 list is not sufficient. Static Excel/CSV publication repeats the same broad-response problem already seen nationally, while a regional catalogue/API is useful only if it has a documented field projection and the retained scope fields themselves are safe.

## Next action

**Do not continue region-by-region by default.** Italy should now be treated as **currently unsupported for funded-project discovery under the absolute zero-PII requirement**, unless a genuinely different source appears with both a field-bounded transport and an explicit pre-publication safety guarantee for sufficiently rich project scope.

No production registry change is made by this note.
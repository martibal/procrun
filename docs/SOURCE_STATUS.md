# Phase A source status

Status date: 2026-09-01.

## Portugal 2030 project discovery

### Confirmed safe-looking public surface

The project-only search surface on Mais Transparência exposes project cards with project title, operation code, expected completion date and funding amount. The inspected project-search page did not expose NIF in its returned project-card content.

Current official surface:

`https://transparencia.gov.pt/pt/fundos-europeus/pt2030/beneficiarios-projetos/pesquisar/projeto/`

The portal currently reports approximately 23,609 funded Portugal 2030 projects.

### Forbidden raw-ingest routes

The official monthly Lists of Approved Operations contain fields including beneficiary name and NIF / Tax Identification Number. They must NOT be downloaded into the Procurement Runway intelligence environment and then column-dropped later.

A full Mais Transparência project detail page also includes a beneficiary section. The portal explicitly supports beneficiaries that can be natural persons. Whole-page detail scraping is therefore NOT an approved production ingestion route under the zero-PII requirement.

Example detail surface inspected:

`https://transparencia.gov.pt/pt/fundos-europeus/pt2030/beneficiarios-projetos/projeto/PACS-FC-00972500/`

It contains the project fields needed by the product, including operation code, funding, execution, dates and summary, but also beneficiary content in the same response.

## Current gate

**A1 Portugal 2030 live collector: OPEN / NOT YET IMPLEMENTABLE.**

Before a production collector is written, one of the following must be proven:

1. a field-projected API / endpoint that returns only the frozen project allowlist; or
2. a project-only source surface that exposes the required project scope and temporal fields without returning beneficiary/contact/tax-identifier content at transport level.

If neither route can be proven, the source fails the product's zero-PII gate even though the data are public.

## First-seen provenance

The monthly approved-operation publications are useful conceptually for first-observed timing, but their files contain prohibited fields. They cannot be ingested to derive first-seen dates.

A separate PII-safe way to establish `first_seen_at` is therefore also required before the Portugal 2030 collector passes A1/A2.

## TED

TED remains structurally suitable because its Search API supports server-side field projection. The production client must request only the frozen TED allowlist and reject schema drift.

## Rule

Public availability is not sufficient. A source is production-safe only if prohibited data never enter the intelligence pipeline in the first place.

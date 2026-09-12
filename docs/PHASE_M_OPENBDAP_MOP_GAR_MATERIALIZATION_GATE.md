# Phase M — OpenBDAP MOP gare materialization gate

Status: **BLOCKED — NO PROVABLE ODATA WIRE SCHEMA FOR SAFE CUP→CIG PROJECTION**

Reviewed: 2026-09-12

## Purpose

OpenBDAP publishes the MOP dataset family `Gare Opere Pubbliche`, including structured procurement concepts such as CUP, CIG and gara publication date. This makes the dataset semantically attractive as a prospective materialization layer for the frozen 12-month MOP cohort.

The gate asks whether ProcRun can prove an exact server-side OData projection before receiving any procurement rows.

## Safety rule

**“Datasikkerheten følger ikke av at kilden er offentlig, den følger av hva vi faktisk lar systemet motta.”**

The GAR datasets also expose identity-bearing and uncontrolled fields. ProcRun may therefore use the route only if the exact OData wire names for the frozen safe allowlist can be established from metadata before `DataRows` is called.

Required projected concepts:

- CUP;
- CIG;
- gara publication date.

Broad GAR download or receive-then-filter processing is prohibited.

## Evidence established

### Dataset semantics — PASS

The official OpenBDAP GAR metadata surface publicly documents `Codice CUP`, `Codice CIG` and `Data Pubblicazione Gara`. It also documents identity-bearing fields in the same dataset family, confirming why field-level pre-receipt projection is mandatory.

### Resource resolution — PASS

The current national GAR download surface resolved an OpenBDAP OData resource key:

`3ddefe62-ae2e-48c3-b0bc-0e25dbc7c66a@rgs`

This establishes a current resource route without downloading the GAR row body.

### Resource-specific metadata — INSUFFICIENT

The resource-specific `MdData` endpoint responded successfully during two qualification attempts, but its metadata representation did not expose an unambiguous CUP wire name to the conservative parser. Both attempts stopped before any `DataRows` request.

### Global OData schema — UNAVAILABLE

A dedicated schema-only run (`openbdap-mop-odata-projection`, run `34686855570`) tested the documented/known OpenBDAP metadata candidates without calling `DataRows`:

- `/ODataProxy/$metadata` → HTTP 500, zero-byte response;
- `/Proxy.svc/$metadata` → HTTP 404.

The artifact `openbdap-mop-gare-schema` recorded:

- `schema_only = true`;
- `datarows_called = false`;
- `identity_fields_received = false`;
- `free_text_received = false`;
- `property_count = 0`;
- `relevant_property_count = 0`.

Artifact ID: `10296145909`  
Artifact digest: `sha256:9f9a39990779070a5fecd7fd2aaa87f32ab1024f2df926d82716da2119c8e022`

## Gate assessment

| Gate | Result | Reason |
|---|---|---|
| CUP/CIG semantic relevance | PASS | Official GAR metadata documents both concepts. |
| Public access / reuse | PASS in principle | OpenBDAP publishes the dataset and catalog/API surfaces for reuse. |
| OData resource resolution | PASS | Current GAR resource key was resolved without row receipt. |
| Exact safe wire schema | **FAIL / NOT PROVEN** | Neither resource metadata nor global `$metadata` exposed an unambiguous machine schema usable by ProcRun. |
| Server-side `$select` safety for GAR | NOT TESTED | ProcRun deliberately did not call `DataRows` without proven wire names. |
| Zero-PII before receipt | PASS for qualification, NOT APPROVED for row ingest | Qualification remained metadata-only. Row ingest stays blocked. |

## Decision

`OPENBDAP_MOP_GAR_MATERIALIZATION = BLOCKED_NO_PROVABLE_WIRE_SCHEMA`

ProcRun must not guess hashed OData field names and must not infer them from another MOP dataset. No GAR `DataRows` request is permitted until already-public metadata establishes the exact wire names required by the frozen allowlist.

The `openbdap-mop-odata-projection` workflow is returned to manual-only diagnostic status.

## What could reopen the gate

Only already-public evidence may reopen this route. A qualifying change would be, for example:

1. OpenBDAP restores a usable OData `$metadata` document that identifies the GAR properties unambiguously; or
2. OpenBDAP exposes equivalent resource-specific machine metadata that maps the public GAR field labels to exact OData wire names.

If that occurs, ProcRun may rerun a single bounded control projection with only CUP, CIG and gara publication date. Until then, the route remains blocked.

## Phase-M consequence

Current materialization candidates are now:

- TED structured CUP linkage: **BLOCKED — zero structured CUP evidence in preregistered sample**;
- ANAC/BDNCP CUP linkage: **BLOCKED — no qualifying pre-receipt projected route**;
- OpenBDAP MOP GAR CUP→CIG linkage: **BLOCKED — no provable GAR OData wire schema**.

The frozen 1,356-CUP prospective MOP cohort remains intact. These gate failures do not show that the projects lack later procurement; they show that ProcRun currently lacks an approved zero-PII observation route for that materialization outcome.

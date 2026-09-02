# Kohesio / EU Knowledge Graph property allowlist

Status date: 2026-09-02.

This file freezes only metadata that has been verified directly from the public EU Knowledge Graph
Wikibase property API through the property-only probe in
`scripts/probe_eukg_property_metadata.ps1`.

It is a research allowlist, not a production `SourceContract`.

## Evidence boundary

The metadata probe used only:

- `wbgetentities` for explicit `P...` property entities;
- `wbsearchentities` with `type=property`; and
- labels/descriptions only.

No project/item entity, SPARQL project query, beneficiary value or broad property walk was requested.

## Frozen safe properties

| Property | EUKG label | Verified description / intended research use |
| --- | --- | --- |
| `P1367` | CCI ID | Identifier used for Kohesio projects. Candidate stable lookup key; Phase 2 must prove that the Portuguese operation code is carried here. |
| `P20` | start time | Operation/project start time. |
| `P33` | end time | Operation/project end time. |
| `P474` | budget | Assigned monetary amount for a project. |
| `P835` | EU contribution | Amount of the budget financed by the European Union. |
| `P836` | summary | Description of the item; candidate operation-scope field. |
| `P1368` | programme | CCI programme a Kohesio project belongs to. |
| `P1584` | fund | Fund this project was financed from. |
| `P605685` | programming period | Programming-period property. The property metadata label is authoritative; Phase 2 must verify returned value semantics. |
| `P192` | NUTS code | Identifier for a region per NUTS. |
| `P1820` | last update | Date a reference was modified, revised or updated. Source metadata only; never reinterpret as `first_seen_at`. |
| `P32` | country | Country of the item; safe but not required in the first Phase 2 smoke test. |
| `P127` | coordinate location | Geocoordinates; safe but omitted from the first Phase 2 smoke test because NUTS is sufficient for the coverage gate. |

`rdfs:label` is additionally allowed in the Phase 2 smoke test only for the already narrowed project
resource, as the candidate operation-name surface. It is not treated as a confirmed canonical
`Operation_Name_Programme_Language` mapping until the returned value is checked against the Portuguese
source.

## Explicitly forbidden

`P841` is verified by the same metadata API as **beneficiary name (string)** with the description
"legal entities who got the subvention". It is forbidden in every ProcRun project query.

The following remain forbidden as query forms regardless of property list:

- `SELECT *`;
- `DESCRIBE`;
- `CONSTRUCT`;
- `?project ?predicate ?value` or equivalent property walks;
- beneficiary, beneficiary identifier/VAT, contact, social-media or person variables;
- download-then-filter handling of a broad project record.

## Still unresolved

The metadata round did not establish a distinct graph property for:

- `Operation_Name_Programme_Language` beyond the candidate `rdfs:label` surface;
- the Kohesio validator's `Total_Eligible_Expenditure_Currency` field; or
- whether `P1367` values exactly equal current Portugal 2030 operation codes.

Those gaps do not justify a broad graph query. The next permitted network action is one exact-code
smoke test against `PACS-FC-01781200`, selecting only the frozen safe variables above. A zero-row result
is evidence of absent coverage or an identifier-mapping mismatch; it must not trigger an automatic
property walk.

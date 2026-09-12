# Phase R — intervention-code mapping review

Status: **REVIEW COMPLETE — NO NEW DOMAIN MAPPINGS ADMITTED**

Reviewed: 2026-09-12

## Scope

This review follows the successful Regione Lombardia Socrata qualification and frozen coverage measurement.
The qualified source provides a safe structured intervention code for 4,178 of the frozen 4,305 Phase R
projects, but source coverage is not equivalent to ProcRun classification coverage.

The only question here is whether any of the 25 observed intervention codes can be mapped
**deterministically and unambiguously to one of the existing ProcRun domains** without project free text,
beneficiary data, inference, or taxonomy expansion.

Existing ProcRun domains are:

- `water_wastewater`
- `rail_transport`
- `ports_coastal`
- `energy_efficiency`
- `resilience_fire`

Authoritative classification source: Regulation (EU) 2021/1060, Annex I, Table 1, current consolidated
version available through EUR-Lex. The regulation defines the intervention fields; the Lombardia source
publishes the same structured codes and descriptions.

## Frozen observed distribution

| Code | Projects | Review disposition |
|---|---:|---|
| 010 | 277 | reject — research/innovation activity, no single existing domain |
| 012 | 65 | reject — research/innovation activity, no single existing domain |
| 013 | 573 | reject — SME digitalisation, no existing domain |
| 016 | 5 | reject — government ICT/e-services, no existing domain |
| 021 | 2,293 | reject — SME business development/internationalisation, too broad |
| 023 | 560 | reject — skills/smart-specialisation, no existing domain |
| 025 | 1 | reject — incubation/start-ups, no existing domain |
| 026 | 30 | reject — innovation clusters/networks, no existing domain |
| 028 | 1 | reject — technology-transfer/cooperation signal, no single existing domain |
| 040 | 114 | keep existing mapping — `energy_efficiency` |
| 042 | 19 | keep existing mapping — `energy_efficiency` |
| 044 | 1 | keep existing mapping — `energy_efficiency` |
| 045 | 8 | keep existing mapping — `energy_efficiency` |
| 067 | 142 | reject — household waste prevention/sorting/reuse/recycling; not water/wastewater |
| 075 | 2 | reject — environmentally friendly production/resource efficiency; broader than energy efficiency |
| 083 | 11 | reject — cycling infrastructure, no existing domain |
| 122 | 2 | reject — education infrastructure, no existing domain |
| 126 | 1 | reject — thematic productive investment, no existing domain |
| 127 | 4 | reject — thematic productive investment, no existing domain |
| 168 | 10 | reject — physical regeneration/security of public spaces, no existing domain |
| 182 | 52 | reject — institutional/programme capacity, no existing domain |
| 189 | 1 | reject — thematic productive investment, no existing domain |
| 190 | 1 | reject — thematic productive investment, no existing domain |
| 191 | 1 | reject — thematic productive investment, no existing domain |
| 193 | 4 | reject — thematic productive investment, no existing domain |

The four admitted codes were already present in `INTERVENTION_FIELD_MAP`; this review does not add them.
All other observed codes remain unmapped.

## Result

The existing frozen map covers 142 Lombardia-overlap projects, or **3.2985%** of the frozen 4,305-project
corpus. The review admits **zero additional codes and zero additional projects**.

The distinction is therefore:

- structured source-data ceiling: **4,178 / 4,305 = 97.0499%**;
- safely mapped coverage under the current five-domain taxonomy: **142 / 4,305 = 3.2985%**.

The 97.0499% figure must never be represented as classified coverage.

## Decision

Phase R cannot reach the 40% target by widening mappings inside the current five-domain taxonomy without
violating evidence-bounded semantics. In particular, high-volume codes `021`, `013`, `023`, `010`, and
`067` do not describe any single existing ProcRun domain.

The next permissible design question is therefore **taxonomy scope**, not looser inference: determine
whether ProcRun should add one or more new procurement-relevant domains that are directly and
unambiguously represented by the official intervention fields. Any taxonomy expansion requires its own
preregistered product/semantic gate and must not retroactively reinterpret the existing five domains.

No production mapping, OPEN/CLOSED semantics, confidence contract, or customer output changes are made
by this review.

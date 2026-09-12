# Phase R — candidate component / CPV design gate

Status: **DIAGNOSTIC ONLY**

Reviewed: 2026-09-12

## Purpose

The frozen Phase R candidate-domain measurement established two public-definition-qualified cohorts:

- `digital_transformation`: intervention `013` + action `1.2.3`, 573 projects;
- `waste_circular_economy`: intervention `067` + action `2.6.2`, 142 projects.

This gate defines conservative procurement-component/CPV candidates for later evidence validation. It does not change the production `ComponentDomain`, phrase rules, OPEN/CLOSED logic, read model or customer output.

## Official CPV basis

The CPV is the EU procurement subject-matter vocabulary defined by Regulation (EC) No 213/2008.

### Digital transformation

The candidate is limited to procurement families that directly identify IT goods or services:

- `302*` — computer equipment and supplies;
- `48*` — software package and information systems;
- `72*` — IT services, including software, data and network services.

No generic consultancy, training, telecommunications or electrical-equipment family is admitted solely because it could appear in a digitalisation project.

### Waste / circular economy

The initial candidate is deliberately narrower than the intervention action itself:

- `90514*` — refuse recycling services.

Broader `905*` waste codes are not admitted at this stage because they also cover collection, disposal, incineration and other waste activities that do not by themselves establish the circular/recycling component qualified by the public action definition.

## Decision rule

The next diagnostic must validate these families against the admitted TED evidence universe and report aggregate counts only. A candidate family may proceed only if:

1. it produces bounded, explainable procurement hits;
2. it does not require free-text semantic inference to establish the component;
3. false-positive review does not show systematic cross-domain ambiguity;
4. production taxonomy remains unchanged until the evidence gate passes.

Failure to reach the Phase R 40% coverage target is not a reason to broaden CPV families beyond their documented procurement meaning.

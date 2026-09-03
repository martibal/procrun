# A1 — PRR Projects source-specific clarification

Status: **PUBLISHED-EVIDENCE QUALIFICATION CLOSED: FAIL / EXTERNAL CONFIRMATION REQUIRED**

This document freezes the final published-evidence qualification for `prr_projects_dados_gov`.
The investigation is closed: no further public-document lookup may promote this source unless genuinely
new authoritative evidence appears. Live ingestion remains prohibited.

## Final published-evidence verdict

As reviewed on 2026-09-03, the PRR Projects candidate does **not** satisfy ProcRun A1 under the absolute
pre-receipt zero-natural-person rule.

The failure is narrow but decisive:

- the dataset-specific metadata still reports `Licença não especificada`;
- the exact Projects machine distribution is a bulk resource rather than a documented server-side
  field-projection contract;
- no source-specific schema/data dictionary proves that every retained structured field and project
  title/summary/scope field is incapable of emitting a natural-person identifier before receipt;
- Recuperar Portugal's own data-protection policy confirms that personal data can be disclosed on a
  public portal and are later suppressed according to the RRF retention rule. Public availability is
  therefore not, by itself, a zero-person-data guarantee.

ProcRun must not download the Projects workbook to discover whether it is safe. That would invert the
required safety boundary.

## What the public evidence does establish

The candidate remains unusually strong on every other dimension:

- Estrutura de Missão Recuperar Portugal publishes separate datasets for Projects, Entities,
  Locations, Public Contracts and related PRR objects;
- public PRR project pages expose commercially useful project-level scope, dates, funding, dimension,
  component, investment and operation code;
- Mais Transparência visibly masks natural-person beneficiary/supplier identities as
  `Dados pessoais protegidos pelo RGPD` and states that those personal data were anonymised;
- Recuperar Portugal states that detailed project, beneficiary and procurement information is updated
  daily through interoperability with Mais Transparência;
- the publisher's official general contact is `info@recuperarportugal.gov.pt`.

Those facts show that a viable safe publication architecture may exist. They do not prove the exact
machine response ProcRun would receive.

## Alternatives checked and rejected

The source search also evaluated whether the blocker could be removed without publisher clarification.
None passes the same contract:

### Mais Transparência rendered project pages

Privacy handling is strong and visibly anonymises natural persons before display, but the portal terms
state that portal content is owned by ARTE or used with permission and do not provide the explicit
commercial-reuse licence required for a paid recurring ingestion product. The page is also not a frozen
machine schema contract.

### Kohesio / EU Knowledge Graph

Server-side SPARQL projection and free reuse are technically attractive. However Cohesion-policy rules
can require publication of natural-person beneficiary names, and no authoritative guarantee was found
that retained operation title/purpose free text can never contain a natural-person identifier. It
therefore cannot replace A1 under ProcRun's absolute rule.

### Generic dados.gov.pt policy

Portal-level policy is insufficient because the terms recognise circumstances in which personal data
may lawfully be published, while the Projects resource itself lacks the necessary field-specific
contract. A consumer-side filter remains prohibited.

## One authoritative response can close A1

No new architecture is required if the publisher confirms the properties below. A response from the
Estrutura de Missão Recuperar Portugal, or the public-data operator speaking authoritatively for this
resource, must establish all of them for the exact production resource:

1. the canonical recurring machine URL/resource and complete schema;
2. whether server-side projection exists; if not, that the complete Projects response itself cannot
   contain natural-person identifiers;
3. specifically, that project title/description/summary/scope is anonymised or otherwise controlled
   **before publication** so a natural-person identifier cannot be emitted;
4. that the same guarantee covers every structured field ProcRun retains;
5. the licence applying specifically to PRR Projects despite the current `Licença não especificada`
   metadata, including permission for commercial reuse and transformation;
6. permission for automated recurring retrieval and any rate/operational limits;
7. the update cadence and stable schema/resource-change mechanism.

## Exact field surface requested

ProcRun needs only:

- operation/project code;
- project title;
- project description/summary/scope;
- project start and end dates;
- approved and executed funding values where available;
- fund/programme/dimension/component/investment/objective/theme;
- region/municipality/NUTS where available;
- publication/first-seen timestamp where source-backed;
- canonical project source URL.

Beneficiary, supplier, contact, person, email, telephone and natural-person tax identifiers are never
requested or permitted.

## Ready-to-send publisher request

Recipient: `info@recuperarportugal.gov.pt`

Subject: `Esclarecimento técnico sobre reutilização do Dataset PRR - Projetos`

> Exmos. Senhores,
>
> Pretendemos reutilizar, de forma automatizada e comercial, exclusivamente informação ao nível dos
> projetos do conjunto de dados «Dataset Estrutura de Missão PRR - Projetos» publicado em dados.gov.pt.
> O nosso sistema tem um requisito absoluto: nenhum dado pessoal de pessoa singular pode ser recebido,
> tratado ou armazenado. Por esse motivo não podemos descarregar primeiro o ficheiro e filtrar depois.
>
> Agradecíamos confirmação, para o recurso de produção desse conjunto de dados, dos seguintes pontos:
> (1) URL/recurso canónico para recolha automatizada e respetivo esquema completo; (2) se os campos de
> nome/título e descrição/sumário/âmbito do projeto, bem como os restantes campos do recurso Projetos,
> são sujeitos a anonimização ou outro controlo antes da publicação de forma a não poderem conter
> identificadores de pessoas singulares; (3) se o recurso pode ser limitado no servidor aos campos de
> projeto ou, não sendo possível, se o recurso Projetos completo tem essa garantia; (4) qual a licença
> aplicável especificamente ao conjunto de dados, que atualmente surge como «Licença não especificada»,
> e se permite reutilização e transformação comercial; (5) se a recolha automatizada recorrente é
> permitida e quais os limites aplicáveis; e (6) como são comunicadas alterações de esquema/recurso.
>
> Os únicos campos que pretendemos utilizar são código do projeto, título, descrição/sumário,
> datas, valores de financiamento/execução, dimensão/componente/investimento, localização agregada e
> URL de origem. Não pretendemos receber quaisquer campos de beneficiários, fornecedores ou contactos.
>
> A confirmação escrita destes pontos permitir-nos-á implementar uma integração que falha fechada se o
> contrato do recurso se alterar.
>
> Com os melhores cumprimentos.

## Approval rule

A1 changes from CONDITIONAL to APPROVED only after the exact resource is green on **RIGHTS, ACCESS,
TRANSPORT and FREE-TEXT SAFETY**. Anything weaker remains FAIL for production.

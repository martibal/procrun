# Portugal national procurement coverage gate

Status: **PUBLISHED-EVIDENCE QUALIFICATION CLOSED: NO SAFE COMPLETE ROUTE / EXTERNAL CONFIRMATION REQUIRED**

This document freezes the final published-evidence investigation of Portuguese national procurement
coverage for the ProcRun `OPEN` invariant. Further public-source searching must not silently weaken the
coverage or privacy contract.

## Why TED alone is insufficient

ProcRun `OPEN` means that no relevant procurement was found in all approved sources required for the
stated coverage boundary. TED is approved and field-projected, but it is the EU publication layer and
is not a complete national register of Portuguese procurement relevant to the original Phase-0
mechanism.

The corrected Phase-0 cohort demonstrated the cost of this distinction. `PACS-FC-04022300` was wrongly
OPEN until Portuguese procedure 3809/2026 was found; the correct conservative project state was PARTIAL.
Production code must therefore never infer complete Portuguese absence from TED pagination alone.

## Final candidate findings

### BASE / IMPIC API — BLOCKED

The official BASE API supports contract and announcement queries and requires IMPIC authorisation for
production access. Official documentation now also confirms that the API fields are the same fields
published in the dados.gov.pt bulk files and that the API is updated daily.

That does not satisfy ProcRun's safety boundary. The documented response example includes identity-
bearing supplier/adjudicatário fields and the API has no documented server-side output projection.
Receiving the broad response and deleting prohibited fields locally is expressly forbidden.

The official BASE documentation also says announcement data in BASE may be less complete and delayed
relative to Diário da República. BASE announcement absence therefore cannot by itself establish the
strongest national announcement-coverage claim.

### BASE / dados.gov.pt announcements — BLOCKED FOR INTELLIGENCE INGEST

A separate official dataset now exists for `Contratos Públicos - Portal Base - IMPIC - Anúncios de
2012 a 2026`. It is nationwide, has historical files, was updated in August 2026 and carries the
resource licence `Outra (Domínio Público)`.

This resolves reuse/history concerns for the dataset, but not the privacy transport gate. The resource
is a broad annual JSON/XLSX download, with no official field-level machine projection or source-specific
statement proving that every received announcement text field is natural-person-free. ProcRun may not
download it merely to inspect and then filter the schema.

### Diário da República / INCM full announcement — BLOCKED

DRE is the official source for current Portuguese public-procurement announcements. Full Part L
announcement pages/documents visibly contain contact-person/service, email, telephone and author fields.
Those responses cannot enter the intelligence plane.

### Diário da República Part L RSS/index — CONDITIONAL, NOT SUFFICIENT

INCM provides an official RSS route for Série II, Parte L - Contratos públicos. This is materially safer
than downloading full notices because it is an index/update surface. Portuguese publication rules also
identify Part L as the section for public-contract formation announcements that require publication in
the official journal.

It still fails the current production gate for three reasons:

1. no authoritative exact XML item schema or zero-natural-person guarantee was found for the RSS/index
   title/summary surface;
2. the RSS is an update feed and no documented historical-completeness contract was found that would
   let ProcRun prove absence back through the required lookback window;
3. Part L covers procedures that require official-journal publication, not every possible Portuguese
   procurement path. It cannot support the stronger statement `component not procured` on its own.

## No silent claims downgrade

Two narrower products would be technically possible, but neither may be adopted without a deliberate
product/validation decision:

- `No relevant TED-covered procurement found as of DATE`; or
- `No relevant publicly announced Part-L competitive procurement found as of DATE`.

Both are weaker than the original national procurement-coverage meaning and cannot inherit the existing
Phase-0 result without a new confirmation. They are therefore not used to force this gate green.

## Exact route required to close the gate

An authoritative IMPIC or INCM response can close the blocker without changing the product if it
identifies a production route that establishes all of the following:

1. recurring automated and commercial reuse is permitted;
2. before receipt, the response contains only a bounded non-personal announcement surface, or the whole
   response is explicitly guaranteed not to contain natural-person identifiers;
3. the route supplies sufficient historical and current national coverage for the exact `OPEN` claim;
4. pagination/completeness semantics are documented so successful completion can be proven;
5. latency/refresh semantics support an explicit `as of` date;
6. schema/version drift can be detected and fails closed.

The minimum useful field surface is announcement ID, publication date, procedure title/object, CPV,
procedure type, value/currency, aggregated place/NUTS, EU/project reference where available and canonical
source URL. Free text may be retained only if it receives the same pre-publication zero-person guarantee.

## Ready-to-send IMPIC request

Official route: IMPIC Helpdesk / `Contratação Pública` form. The legacy general email is no longer an
active support channel according to IMPIC's current FAQ.

Subject: `Esclarecimento técnico sobre API/Anúncios do Portal BASE`

> Exmos. Senhores,
>
> Pretendemos utilizar de forma automatizada informação de anúncios de contratação pública do Portal
> BASE para verificar, por data, se já existe procedimento relevante associado a projetos públicos.
> O nosso sistema tem um requisito absoluto: nenhum dado pessoal de pessoa singular pode ser recebido,
> tratado ou armazenado, pelo que não podemos obter uma resposta ampla e filtrar localmente.
>
> Solicitamos esclarecimento sobre a existência de um endpoint, vista ou modalidade da API que devolva
> exclusivamente campos não pessoais de anúncio: identificador/número do anúncio, data de publicação,
> objeto/título do procedimento, CPV, tipo de procedimento, valor, localização agregada/NUTS, eventual
> referência a fundos/projeto e URL oficial. Caso não exista projeção de campos, agradecemos confirmação
> sobre se a resposta de anúncios correspondente é garantidamente isenta de identificadores de pessoas
> singulares, incluindo nos campos de texto.
>
> Para podermos utilizar a ausência de resultados de forma auditável, necessitamos ainda de saber qual a
> cobertura histórica/nacional da rota, como é sinalizada paginação/completude, qual a latência esperada,
> e se a reutilização automatizada/comercial desses campos é autorizada no âmbito do acesso concedido.
>
> Pretendemos excluir integralmente adjudicatários/fornecedores, pessoas de contacto, emails, telefones,
> moradas pessoais e quaisquer outros identificadores de pessoas singulares antes de qualquer byte ser
> recebido pelo nosso ambiente analítico.
>
> Com os melhores cumprimentos.

## Ready-to-send INCM request

Recipient/contact route: Diário da República customer/contact channel; current INCM material exposes
`geral@diariodarepublica.pt` for Diário da República service contacts.

Subject: `Esclarecimento técnico sobre feed/índice da Série II - Parte L`

> Exmos. Senhores,
>
> Pretendemos consumir automaticamente apenas metadados não pessoais dos anúncios publicados na Série II,
> Parte L - Contratos públicos, sem descarregar o texto integral dos anúncios. O nosso sistema não pode
> receber qualquer dado pessoal de pessoa singular.
>
> Agradecíamos confirmação do esquema oficial do feed RSS/índice da Parte L e se os itens devolvidos
> (identificador, data, entidade emitente, título/sumário e ligação) são sujeitos a uma regra que garanta
> a inexistência de identificadores de pessoas singulares antes da publicação. Solicitamos também
> indicação sobre uma rota oficial de arquivo/histórico com o mesmo esquema, respetiva cobertura,
> paginação/completude, frequência de atualização e condições de reutilização automatizada/comercial.
>
> Não pretendemos consumir os documentos completos, que incluem campos de contacto; apenas uma superfície
> de índice comprovadamente não pessoal e auditável.
>
> Com os melhores cumprimentos.

## Production invariant

Until an exact national route passes the six requirements above:

- positive approved evidence may close a component when the matching rules are satisfied;
- TED-only or RSS-only absence may not create the original national `OPEN`;
- components requiring that absence proof remain `UNRESOLVED`;
- A20 remains blocked.

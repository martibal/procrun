# ProcRun 2.0 — Kravspesifikasjon: Tidsbesparelse og oversikt som kjerneverdi

**Hva som endres fra 1.0:** kjernepipeline, datakilder og sikkerhetsregler endres ikke — alt det står
fast. **Produktets datakontrakt og presentasjonsarkitektur utvides derimot reelt:** source evidence blir
førsteklasses data med egen proveniens, ProcRun-tolkning og kildetekst må holdes eksplisitt adskilt,
original/oversettelse må håndteres separat, og tabellen får nye obligatoriske felt. Dette er ikke en ren
ompakkering av eksisterende arkitektur — det er en utvidelse av den. OPEN/CLOSED/UNRESOLVED-dommen
nedgraderes fra hovedprodukt til hjelpelag, inntil A21 beviser at den fortjener hovedrollen.

**Premisset denne versjonen bygger på:** produkter som sparer kunden for tid og gir bedre oversikt
selger godt, uavhengig av om de tilfører ny innsikt kunden ikke kunne funnet selv. Det er allerede bevist
kommersielt i en rekke etablerte kategorier. ProcRun 2.0 skal selges som **nettopp dette** — ikke som et
beslutningsverktøy som påstår seg smartere enn det empirisk er bevist å være i dag.

---

## 1. Ny produktdefinisjon

**Gammel definisjon (1.0):** *"ProcRun forteller deg hva som fortsatt er å kjøpe."*

**Ny definisjon (2.0):**

> ProcRun scanner tusenvis av EU-finansierte infrastrukturprosjekter i Lombardia daglig, filtrerer dem
> ned til de få som faktisk er relevante for det du selger, og samler prosjektbeskrivelse, finansiering
> og relevant TED-anskaffelsesdata på ett sted — med kildeteksten rett ved siden av, slik at du aldri
> trenger å lete deg gjennom rådataene selv. ProcRuns egen vurdering av status vises som et hjelpemiddel,
> ikke som en påstått fasit.

Dette er det som faktisk er bevist: 4 631 finansierte prosjekter → 81 med identifiserte,
kildedokumenterte kjøpsbehov. **Dette er empirisk dokumentasjon på at ProcRun kan redusere
søkeuniverset kraftig** — det er noe annet, og svakere, enn å si at vi allerede har bevist at kunder
vil betale €149/mnd for nettopp dette. Reduksjonen krever ingen forbedring i klassifiseringspresisjon
for å være reell; om den er kommersielt tilstrekkelig alene, er fortsatt uverifisert.

---

## 2. Hva kunden faktisk kjøper — omprioritert

| Prioritet | Element | Status |
|---|---|---|
| **1 (hovedverdi)** | Daglig, automatisk innsnevring: 4 631 → et lite, relevant utvalg | Bevist, produksjonskjørt |
| **2 (hovedverdi)** | Organisert tabellvisning: prosjekt, finansiering, kildetekst, TED-funn samlet | Bygges nå (§4) |
| **3 (hjelpelag)** | ProcRuns tolkning (OPEN/CLOSED/UNRESOLVED) | Vises, men tydelig merket som hjelpemiddel — ikke hovedbudskap |
| **4 (fremtidig hovedverdi)** | Tolkningen som pålitelig nok til å stå alene | Betinget av A21 = GO |

---

## 3. Hvorfor dette faktisk er bedre oversikt enn konkurrentene, uavhengig av tolkningskvalitet

Dette er en påstand som kan forsvares **i dag**, uten å vente på A21:

- **TedScout, Mercell og lignende viser anbud som allerede er kunngjort.** De starter ett steg senere i
  kjeden enn ProcRun. ProcRun starter ved finansieringsvedtaket, før anbudet nødvendigvis eksisterer —
  det er en strukturell, verifiserbar forskjell i *hva slags oversikt* som gis, ikke en påstand om at
  ProcRun er "smartere."
- **Ingen av de konkurrentene vi til nå har undersøkt (TedScout m.fl.) samler finansieringsdokumentasjon,
  uttrukket kjøpsbehov og TED-status i én tabellrad med kildetekst synlig.** Dette er en organiserings-
  og presentasjonsfordel, bevisbar ved å vise produktet. **Dette er ikke en verifisert påstand om hele
  markedet** — kun om de konkurrentene som faktisk er undersøkt til nå — og skal ikke fremstilles som
  et absolutt "ingen andre gjør dette" før en systematisk markedsgjennomgang bekrefter det.
- **Konkurrentene krever at kunden selv vurderer relevans mot en lang liste.** ProcRuns
  innsnevringssteg (4 631 → 81) er i seg selv den tidsbesparelsen konkurrentene ikke systematisk
  tilbyr på dette stadiet i anskaffelseskjeden.

Denne argumentasjonen skal være markedsføringens hovedlinje — **ikke** "vår algoritme er mer presis enn
deres."

---

## 4. Tabellvisning — ny hovedkomponent

Erstatter den enkle Opportunity Feed-listen med en tabell der hver rad inneholder, i denne
prioriterte rekkefølgen:

1. **Prosjekt** (tittel, finansieringsbeløp, region) — alltid synlig, alltid fra godkjent kilde
2. **Kildetekst** — relevant utdrag fra prosjektdokumentasjonen, ordrett, alltid synlig som egen
   kolonne, **ikke gjemt bak et klikk**
3. **TED-status** — observerbare fakta, **aldri** et binært "funnet ja/nei" (se §4.1)
4. **ProcRun-tolkning** — vises i en tydelig avgrenset, mindre fremtredende kolonne, alltid merket
   *"ProcRun interpretation — helper, not a definitive answer"*

**Regel:** kildetekst-kolonnen vises **for alle rader**, ikke bare UNRESOLVED-rader. Dette er den
direkte konsekvensen av at kildetekst nå er hovedprodukt, ikke en unntaksmekanisme for usikre
tilfeller. Diskusjonen fra forrige runde om å skjule kildetekst ved UNRESOLVED er dermed foreldet —
det er ikke lenger en fallback, det er standardvisningen.

**Visningskrav:** kildeteksten skal alltid være tilgjengelig direkte i raden uten at brukeren må åpne
en separat detaljside. På små skjermer eller ved lange utdrag kan teksten trunkeres til et meningsfullt
utdrag, men fulltekst skal kunne ekspanderes **inline i samme rad**.

### 4.1 TED-status — konservativ semantikk, ikke binær

**Aldri** "funnet: ja/nei." "Nei" kan lett leses som "ingen kunngjøring finnes" — noe systemet ikke kan
vite. Tillatte verdier:

- `Matched tender identified`
- `No matching tender identified`
- `Match uncertain`

Vist separat, som egne observerbare fakta, ikke sammenslått med tolkningen:
`award notice identified` (ja/nei/uncertain), `deadline`, `publication date`, `notice ID`.

### 4.2 Ingen kolonne uten operasjon

Ingen kolonne skal vises i hovedtabellen med mindre brukeren faktisk kan filtrere, sortere, søke eller
handle på verdien. Gjelder eksplisitt: confidence, ProcRun-tolkning, TED-match, region, dato,
kildespråk, evidens-tilstedeværelse. Confidence vises primært som **High/Medium/Low med forklaring**,
aldri som en rå statistisk verdi i hovedtabellen (eksakt score kan ligge i detaljvisning/tooltip).

### 4.3 Italiensk/engelsk-bryter

- Italiensk = original, autoritativ kildetekst
- Engelsk = oversettelse av nøyaktig samme utdrag, alltid merket *"Translated from Italian"*
- Bryter direkte i tabell/detaljvisning
- Oversettelsen erstatter aldri originalen som evidens — originalen er alltid tilgjengelig

### 4.4 Evidensuttrekk-kontrakt — obligatorisk funksjonell komponent

ProcRun skal identifisere de 1–3 setningene i prosjektdokumentasjonen som er mest relevante for
anskaffelsesstatus, planlagt kjøp, utlysning, kontrakt, tildeling eller gjennomføring. Hvert uttrekk
skal ha: ordrett originaltekst, eksakt span (start/slutt-posisjon i kilden), kildereferanse,
dokumentdato, dokument-ID/URL, originalspråk, og eventuell oversettelse per §4.3. Hvis systemet ikke
finner et forsvarlig relevant utdrag, skal det ikke finne på ett.

---

## 5. Tolkningslaget — degradert, men ikke fjernet

OPEN/CLOSED/UNRESOLVED beholdes, fordi det fortsatt gir reell verdi som **prioriteringshjelp** — en
kunde med 20 rader foran seg drar nytte av en antydning om hvor de bør se først, selv om antydningen
ikke er ufeilbarlig.

**Krav til visuell og språklig underordning:**
- Tolkningskolonnen skal aldri ha større visuell vekt enn kildetekst-kolonnen
- Ingen fargekoding som gir inntrykk av sikkerhet tolkningen ikke har (jf. eksisterende
  `--verified-green`-regel: grønn er fortsatt kun for faktisk kildeverifisert TED-treff, ikke for
  ProcRuns egen sektor-/statustolkning)
- All tolkningstekst skal inneholde ordet *"interpretation"* eller tilsvarende eksplisitt hjelpemerking
  — aldri presenteres som et faktum på linje med kildeteksten

---

## 6. UNRESOLVED mister sin spesialstatus

Med kildetekst som standard, ikke unntak, forsvinner UNRESOLVED-problemet fra forrige rundes diskusjon.
En UNRESOLVED-rad er nå bare en rad der **tolkningskolonnen** sier "usikker," mens **kildetekst- og
TED-kolonnene** viser nøyaktig det samme som for enhver annen rad. Kunden mister ingenting ved
UNRESOLVED utover selve etiketten — de har fortsatt prosjektet, kildeteksten og TED-status foran seg.

Dette betyr at §7-splitten fra forrige dokument (evidens vs. ingen evidens) fortsatt er nyttig
informasjon, men ikke lenger avgjørende for om produktet er brukbart — det er nå kun én av flere
kolonner, ikke et enten/eller for hele raden.

---

## 7. Markedsførings- og prisingskonsekvens

**Landingsside, methodology og pricing skal oppdateres til å lede med innsnevrings-/oversiktsverdien,
ikke tolkningsverdien.** Konkret endring av den frosne hero-teksten fra tidligere runde:

**Gammel (1.0):**
> *"Find what funded infrastructure projects still need to buy."*

**Ny (2.0), forslag:**
> *"See exactly which of Lombardia's funded infrastructure projects are relevant to what you sell —
> without reading through thousands of documents yourself."*

Understreken skal nevne innsnevringstallet konkret (f.eks. *"ProcRun screens thousands of funded
projects and narrows them to what matters for your business"*) — ikke love en status-konklusjon som
hovedbudskap.

**Prisankeret beholdes foreløpig på €149/mnd**, forankret mot de samme sammenlignbare produktene som
tidligere (TedScout, Stotles), **og valideres separat mot faktisk betalingsvillighet.** At
tidsbesparelse alene forsvarer nettopp dette prisnivået er en hypotese, ikke et empirisk bevist krav.
Det som endres nå er *hva* kunden betaler for; *hvor mye* de faktisk vil betale gjenstår å teste.

---

## 8. A21 deles i to separate valideringsgater

Med kildetekst som nytt hovedprodukt (§4.4) trenger det sin egen valideringsgate — like reell som
tolkningsgaten, men målt på noe annet.

### 8.1 Gate A21a — Evidence Retrieval (nytt, dekker hovedproduktet)

Måler om ProcRun finner **riktig** tekst, ikke om tolkningen er riktig:
- Finner systemet de riktige 1–3 setningene?
- Er de faktisk relevante for anskaffelsesstatus?
- Er de ordrette, verifiserbart mot originalkilden?
- Peker de til korrekt kildedokument?
- Forekommer ingen PII i uttrekket?
- Er irrelevante/støyende utdrag sjeldne nok?

**Hard-gate-krav:** A21a kan ikke erklæres GO før numeriske terskler er preregistrert og frosset
**før** sluttevalueringen. Minimum skal følgende ha eksplisitte terskler: exact source-span validity,
source-document correctness, PII violations, hallucinated/rewritten evidence, relevant-evidence recall
og irrelevant-evidence rate. Tersklene skal ikke fastsettes retrospektivt etter at sluttresultatene er sett.

### 8.2 Gate A21b — Interpretation (den opprinnelige A21-spesifikasjonen, uendret)

Måler om OPEN/CLOSED/UNRESOLVED-dommen er korrekt, per den allerede frosne
`CLASSIFICATION_ENGINE_VALIDATION_GATE.md`-spesifikasjonen — ingen endring i krav eller terskler.

**Konsekvens:** A21b er ikke lenger en blokkering for lansering av ProcRun 2.0. **A21a er derimot
en nødvendig produktkvalitetsgate for 2.0-posisjoneringen.** Lansering krever i tillegg at øvrige
sikkerhets-, datakilde-, drifts- og kommersielle release-gates er oppfylt.

**A21b forblir forutsetningen for å kunne oppgradere produktet fra "tidsbesparelsesverktøy" til
"beslutningsstøtteverktøy"** og løfte tolkningen tilbake til hovedbudskap.

Når A21 = GO, kan tolkningskolonnen igjen løftes til hovedbudskap, prisen kan potensielt økes, og
markedsføringen kan legge til "og vi kan fortelle deg status med dokumentert presisjon" som et
sekundært, sterkt salgsargument. Inntil da forblir 2.0-posisjoneringen den kommersielt ærlige og
salgbare varianten.

---

## 9. Akseptansekriterier

1. Tabellvisningen viser kildetekst for **alle** rader, ikke kun UNRESOLVED
2. Tolkningskolonnen er visuelt og språklig tydelig underordnet kildetekst- og TED-kolonnene
3. TED-status bruker aldri binært "funnet ja/nei" — kun de tre tillatte verdiene i §4.1
4. Hver kolonne i hovedtabellen er filtrerbar, sorterbar eller søkbar (§4.2) — ingen unntak
5. IT/EN-bryter fungerer i tabell og detaljvisning, med korrekt "Translated from Italian"-merking
6. Evidensuttrekk følger §4.4-kontrakten fullt ut, inkludert eksakt span og kildereferanse
7. Ingen kundevendt tekst (landing, methodology, pricing) leder med en presisjons- eller
   statuspåstand som hovedbudskap
8. Hero-tekst og produktbeskrivelse er oppdatert til å fremheve innsnevring/tidsbesparelse først
9. Konkurrent- og prisclaims i §3/§7 er formulert med riktig usikkerhetsforbehold, ikke som bevist fakta
10. A21a (Evidence Retrieval) er definert som egen, separat gate og kan bestås uavhengig av A21b
11. A21a har preregistrerte, frosne numeriske terskler før sluttevaluering
12. Kildetekst er tilgjengelig direkte i raden; eventuell trunkering kan kun ekspanderes inline, ikke kreve separat detaljside
13. Eksisterende zero-PII, no-contact og evidenskjede-krav er uendret og re-verifisert etter endringen

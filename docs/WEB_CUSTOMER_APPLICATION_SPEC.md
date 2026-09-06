# ProcRun — Kravspesifikasjon: Kundeapplikasjon (Webfase)

**Status:** BYGGEKLAR
**Forutsetning:** `A8`/`A19` (ikke-web-produktet: datakilder, personvernarkitektur, produksjonsdrift) er PASS og ligger utenfor denne specens omfang — den skal ikke endres eller re-verifiseres av webteamet.
**Omfang:** Alt som gjenstår for at ProcRun kan gå til betalende kunder, avgrenset til Lombardia.

---

## 1. Rammebetingelser som gjelder hele denne specen

1. **Null kontakt-regelen gjelder fortsatt.** Ingen del av webfasen skal innebære kontakt med kilde-eiere, myndigheter eller kunder for å løse en utviklingsoppgave. Support på innkommende kundehenvendelser er unntatt (reaktivt, ikke oppsøkende) og først relevant etter lansering.
2. **Ingen rå kildedata skal noensinne nå browser eller API-lag.** Eneste tillatte datakontrakt er `src/procrun/read_model.py` (`customer-runway-v1`). Dette er frosset og skal ikke endres av webteamet uten egen godkjenningsprosess.
3. **Konto-/faktura-/betalings-PII skal ligge i et adskilt kontrollplan**, aldri i intelligence-databasen eller modellkonteksten.
4. **Kostnadstak:** kjerneinfrastruktur skal holdes under 400 kr/mnd, varsel ved overskridelse, ingen arkitekturendring over 500 kr/mnd uten eksplisitt gjennomgang. Stripe/betalingsgebyrer spores separat fra dette taket.
5. **Normativ kunde-/datagrense:** `docs/CUSTOMER_DATA_AND_COMMERCIALIZATION_CONTRACT.md` og `docs/BUILD_GATES.md` gjelder foran denne webspecen ved enhver konflikt om kilder, personvern, rettigheter, attribusjon, eksport, kundevendt datainnhold eller kommersielle påstander. Denne specen kan aldri utvide en kilde-, data- eller kundesikkerhetsgrense.

---

## 2. Geografisk og datamessig sannhetsgrense — skal reflekteres presist i UI fra dag én

**Aktiv dekning ved lansering: kun Lombardia (PR FESR Lombardia 2021-2027) + TED-scoped søk (paneuropeisk, men kun "ingen treff funnet i TED"-negativ dekning, ikke positiv fullstendighetsgaranti).**

Følgende setninger er frosset og skal brukes ordrett der relevant, ikke omskrives av webteamet:

- **TED-attribusjon:** *"Source: Tenders Electronic Daily (TED), Publications Office of the European Union. ProcRun transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement."*
- **OpenCoesione-attribusjon:** *"Source: OpenCoesione, Lista beneficiari e operazioni 2021-2027 (PR FESR Lombardia), used under CC BY 4.0. ProcRun transforms and classifies the source data; the derived analysis is not an official OpenCoesione, Italian-government or EU publication or endorsement."*
- **TED OPEN-definisjon:** *"No relevant procurement found in TED as of DATE."* — skal aldri forkortes til en nasjonal eller universell fraværspåstand.
- **Datafylling-forbehold (nytt, obligatorisk):** *"Dekningen reflekterer det italienske overvåkingssystemets nåværende fyllingsgrad for 2021–2027-perioden og vil vokse i takt med at flere prosjekter registreres nasjonalt."*

Onboarding, region-/programvalg og methodology-siden skal eksplisitt si **"Lombardia"**, aldri "Italia" som en uklar samlebetegnelse, inntil flere regioner er formelt aktivert (jf. egen, pågående, ikke-blokkerende datautvidelsesoppgave).

**Terminologiregel:** interne analysebegreper (f.eks. "CPV-blind signal") skal **aldri** brukes i kundevendt tekst — verken på landingssiden, i demo, methodology eller produktkopi generelt. De kan fortsatt brukes i intern teknisk dokumentasjon. Kundevendt forklaring av differensieringen skal alltid være konkret og jargongfri, i retning av: *"ProcRun starter i finansierte prosjekter og dokumentert behov, ikke bare i allerede publiserte tenders."* Ingen kunde skal måtte lære ProcRuns interne terminologi for å forstå verdiforslaget.

---

## 3. Informasjonsarkitektur — frosset navigasjonsstruktur

**Offentlig hovednav:**

```
[ProcRun-logo → Home] · Demo · Methodology · Pricing · Sign in
```

Ingen egen "Produktforklaring"-side ved lansering — Home skal selv bære forklaringen av de to
hoveddelene (Opportunity Feed + Market Intelligence), hvem produktet er for, og hvorfor signalet er
annerledes. En egen `/product`-side bygges **kun** hvis Home i praksis blir for salgsorientert til å
forklare arbeidsflyten ordentlig — ikke som en standard del av launch-scopet.

**Innlogget hovednav:**

```
[ProcRun-logo → Opportunities] · Opportunities · Saved · Market          Supplier Profile · Account
```

Ekstremt stramt, med hensikt. **Opportunity Feed skal aldri kalles "dashboard"** noe sted i UI eller
dokumentasjon — det er produktets primære arbeidsflate, ikke en oversikts-KPI-side. "Dashboard" er
reservert for Market Intelligence, der formatet faktisk hører hjemme.

**Ikke-navigerbare detaljsider:** `/app/opportunities/[id]` (nås fra feeden, ikke fra hovednavigasjonen).

**Supplier Profile og Account skal aldri slås sammen til én "Settings"-side.** Supplier Profile
påvirker hva ProcRun viser kunden; Account handler om abonnement, betaling og brukeradministrasjon. De
er to forskjellige konsepter og skal forbli det i UI-strukturen.

**Utsatt til etter lansering, ikke en del av launch-scopet:** About, Contact, Support som egne
navigasjonssider.

### 3.1 Demo — definert som en salgsflate, ikke "en side blant flere"

Demo er sannsynligvis stedet en potensiell kunde faktisk bestemmer seg. Kravene:

- Bruk **ekte Lombardia-records** hentet gjennom den samme frosne read model-kontrakten som kundeapplikasjonen for øvrig — ikke skjermbilder, ikke syntetiske eksempler, med mindre et konkret reelt tilfelle ikke lar seg vise av lisens- eller PII-grunner (i så fall: dokumenter avviket eksplisitt i koden, ikke bare stilt inn i taushet).
- Brukeren skal kunne klikke seg gjennom **full customer-safe Opportunity Detail** for det begrensede offentlige utvalget. Evidens skal ikke avkortes, sladdes eller låses bak betaling for et tilfelle som først er gjort offentlig.
- **Krever ingen innlogging.** Det betyr at attribusjonstekstene i §2 skal rendres **på selve `/demo`-siden** og på eventuell offentlig detaljvisning — en besøkende kan lande direkte der og skal likevel se korrekt kildeattribusjon der dataene faktisk vises.
- Demoens offentlige utvalg skal være eksplisitt kontrollert og begrenset. Det skal kunne oppdateres i takt med faktisk datadekning, men må aldri være en automatisk offentlig speiling av hele den betalte feeden.
- Offentlige URL-er, API-endepunkter, sitemap, søk eller ID-enumerering må ikke gjøre det mulig å rekonstruere hele corpus uten autentisering.

---

### 3.2 Full sideskjelett — rutekart og lenkematrise

Formål: alle sider skal eksistere som ruter med korrekt navigasjon mellom dem **før** detaljert
innhold bygges per side. Dette er rekkefølgen: skjelett først, innhold etterpå.

### Offentlige ruter

| Rute | Lenkes fra | Lenker videre til | Skjelett-status ved "ferdig skjelett" |
| --- | --- | --- | --- |
| `/` (Home) | Alle sider (logo) | Demo, Methodology, Pricing, Sign in | Frosset hero-tekst (§5 visuell spec) + ett ekte opportunity-eksempel |
| `/demo` | Home-nav, header-CTA | Offentlig detalj for kontrollert utvalg, Sign in, Pricing | Begrenset offentlig utvalg med ekte data og full customer-safe detail depth; ingen innlogging kreves |
| `/methodology` | Home-nav | Kildeattribusjon-lenker (ekstern), Pricing | De frosne attribusjons-/forbeholds-setningene fra §2, relevansbånd-forklaring |
| `/pricing` | Home-nav, Demo, footer | Sign in / registrering | €149/mnd, hva som er inkludert |
| `/login` (Sign in) | Home-nav, Pricing, Demo | Onboarding (`/app/onboarding`) ved første innlogging, ellers `/app` | Autentiseringsskjema, ingen ekstra innhold nødvendig i skjelettfasen |
| `/terms` | Footer | — | Juridisk tekst, kan være placeholder til §7-portene er grønne |
| `/privacy` | Footer | — | Samme som over |

### Autentiserte ruter

| Rute | Lenkes fra | Lenker videre til | Skjelett-status |
| --- | --- | --- | --- |
| `/app/onboarding` | Første innlogging (automatisk) | `/app` (etter fullført profil) | Supplier Profile-oppsett — obligatorisk før feed vises |
| `/app` (Opportunities — **aldri kalt "dashboard"**) | Hovednav | `/app/opportunities/[id]` | Feed-liste med filterrad, tom-tilstand skrevet per visuell spec |
| `/app/opportunities/[id]` | Kun fra feed/saved, ikke egen navlenke | Tilbake til feed, "Show evidence"-utvidelse | Full evidenskjede-layout |
| `/app/saved` | Hovednav | `/app/opportunities/[id]` | Liste, tom-tilstand ("No saved opportunities yet") |
| `/app/market` (Market Intelligence — dashboard-formatet hører hjemme her) | Hovednav | — | Aggregert graf/tabell |
| `/app/profile` (Supplier Profile) | Høyre nav | — | Skjema, adskilt fra Account |
| `/app/account` | Høyre nav | Stripe kundeportal (ekstern, når §7-port 3 er klar) | Abonnementsstatus, kan vise placeholder før betaling er koblet på |

### Eksplisitt regel for skjelettfasen

En rute regnes som **skjelett-ferdig** når: (1) den er nåbar fra minst én annen side i matrisen over,
(2) den bruker riktig navigasjonskomponent fra visuell kravspec §3/§4.6, (3) den viser enten ekte data,
en korrekt skrevet tom-tilstand, eller en tydelig merket placeholder — **aldri** en blank hvit side eller
en "Coming soon"-tekst uten kontekst. Detaljert innhold (fullstendig markedsintelligens-visualisering,
komplett Stripe-integrasjon osv.) kommer i neste fase, per side, i den rekkefølgen dere selv prioriterer.

---

## 4. Kjernefunksjoner — de seks opplevelsene

### 4.1 Supplier Profile

Onboarding: firmanavn, målmarked (Lombardia), produktkategorier fra taksonomien, valgfrie CPV-inklusjoner/-eksklusjoner, valgfritt verdiintervall. **Ingen krav om navngitte ansatte, personlig e-post/telefon.**

### 4.2 Opportunity Feed

**Kalles aldri "dashboard"** — dette er produktets primære arbeidsflate. Standardvisning: **High + Medium**-relevans (jf. §5). Filtrerbar på infrastruktursektor, CPV, verdi, prosedyrestadium, relevansbånd og dokumenterte demand-kategorier.

### 4.3 Opportunity Detail

Full evidenskjede per mulighet: kilde, publiseringsdato, alle uttrukne requirements med match-status, eksakt kildetekst-span, TED-/OpenCoesione-referanse, metodikknotat, as-of-tidsstempel, uforanderlig versjons-ID. UI skal tydelig skille **source facts** fra **ProcRun-klassifiseringer**.

For et record som inngår i det eksplisitt godkjente offentlige utvalget, skal offentlig Opportunity Detail ha **samme customer-safe detail depth** som den betalende brukeren ser for det samme recordet. Betaling skal ikke låse opp en rikere source/privacy-grense for ett enkelt tilfelle.

### 4.4 Saved Opportunities

Enkel arbeidsliste. Ikke CRM — ingen kontaktfelt, ingen pipeline-stadier utover "lagret/sett".

### 4.5 Market Intelligence

Aggregert historikk fra samme datagrunnlag: volumtrend, verditrend (med synlig dekningsandel — manglende verdi vises aldri stille som null), topp-kategorier, topp-kommuner/provinser i Lombardia.

### 4.6 Export

CSV-eksport av kundens egne lagrede/filtrerte resultater. Ingen eksport av felt utenfor den frosne read model-kontrakten.

### 4.7 Gratis vs. betalt — permanent depth/breadth-grense

Følgende to prinsipper er **låst ordrett** og skal fungere som testbare produktregler:

> **ProcRun does not charge customers to reveal the evidence behind an individual opportunity. ProcRun charges for continuously finding, organizing, filtering and matching opportunities across the market.**

> **Public and paid Opportunity Detail must use the same customer-safe evidence contract. Payment may widen access to the corpus and workflow, but never widen the source/privacy boundary for an individual record.**

Dette implementeres som et eksplisitt skille mellom **full detail depth** og **full corpus breadth**:

**Gratis/offentlig:**

- et kontrollert, begrenset utvalg ekte Lombardia-opportunities;
- full customer-safe prosjekttittel, godkjente finansierings-/lokasjons-/program-/referansefelt;
- full customer-safe evidenskjede uten teaser, blur eller "unlock evidence"-mønster;
- eksakt godkjent kildetekst-evidens, identifisert behov, TED-sjekkresultat, begrunnelse og dekningsforbehold;
- kildeattribusjon og godkjente lenker til primærkildene;
- ingen personlig relevansvurdering uten Supplier Profile.

**Betalt:**

- hele tilgjengelige opportunity-corpuset gjennom den løpende feeden;
- supplier-profile matching og personlig High/Medium/Low-relevans;
- filtrering og søk på tvers av corpus;
- løpende tilgang til nye opportunities etter hvert som de publiseres og behandles;
- Saved Opportunities;
- Market Intelligence;
- customer-safe CSV-eksport.

**Ikke tillatt:**

- å gjøre alle opportunity-ID-er anonymt nåbare, enumerable eller SEO-indekserbare slik at hele feeden kan rekonstrueres uten abonnement;
- å bruke en betalingsmur til å skjule evidens for et record ProcRun allerede har valgt å vise offentlig;
- å gi betalende kunder et bredere felt-/PII-/source-contract-sett for samme record enn det customer-safe read model tillater;
- å omtale gratislaget som en avkortet eller "light" evidensversjon;
- å bruke varsling/alerts som launch-pricing-argument før en faktisk, testet varslingsfunksjon er bygget og godkjent.

**CTA-regel på offentlig detail:** CTA skal selge automatisering og breadth, ikke skjult fakta. Foretrukket retning er f.eks. **"Find opportunities like this for your business"** eller **"See all opportunities matched to your supplier profile"**. Ikke bruk CTA-er av typen "Unlock full evidence".

**SEO-regel:** et begrenset offentlig utvalg kan være indekserbart for å dokumentere produktets kvalitet og bygge organisk synlighet. SEO-indeksering skal aldri automatisk følge hele corpus eller gjøre corpus-discovery mulig gjennom sitemap, ID-sekvenser, API-responser eller annen anonym enumerering.

**Eksplisitt utenfor omfang:** CRM, budskriving, kontakt-/vinnerdatabase, generelt EU-anbudssøk, prosjekt-innsendingsverktøy.

---

## 5. Relevansmodell — implementeres eksakt slik, ikke tolkes på nytt

| Bånd | Krav | Synlig i standardfeed? |
| --- | --- | --- |
| **High** | CPV/domene/geografi-match **+** dokumentert demand-tag med eksakt kildetekst-evidens | Ja |
| **Medium** | CPV/domene/geografi-match, **uten** krav om demand-tag-evidens | Ja |
| **Low** | Svak/delvis match (kun geografi, eller bredt domene uten CPV-spesifisitet) | Nei — skjult som standard |
| **Not relevant** | Ingen meningsfull match | Ekskludert |

Manglende demand-tag skal aldri fremstilles som "ingen behov" — kun at kildeteksten ikke ga tilstrekkelig dokumentasjon.

**Kalibrert eksempel — bruk konsekvent i UI, demo-modus og markedsføringstekst:**

> **[Prosjekttittel]** — [Kommune], Lombardia · [Verdi hvis tilgjengelig]
> **Demand identified:** [ett tag]
> **Evidence:** "[eksakt kildetekst-utdrag]"
> *Merk: færre enn 1 av 50 muligheter viser mer enn ett dokumentert behov samtidig.*

Bruk **aldri** et eksempel med to eller flere demand-tags som standardillustrasjon.

---

## 6. Hva som eksplisitt ikke skal loves — gjelder all kundevendt tekst

Ingen påstand om: fullstendig italiensk eller portugisisk anskaffelses-/finansieringsdekning, forkjøpsrett før publisering, fullstendig komponentdekomponering, at alle relevante muligheter får demand-tags, garantert budkvalifisering, vinnersannsynlighet, EU/TED/OpenCoesione-godkjenning, eller sanntidsovervåking/varsling med mindre arkitekturen faktisk leverer og funksjonen er testet og godkjent.

---

## 7. Launch-porter — obligatorisk før checkout aktiveres (kan bygges parallelt med §3, men skal være grønne før betaling)

1. **Juridisk enhet:** endelig registrert selskap/merchant-identitet
2. **Vilkår & personvern:** publiserte Terms/Privacy-sider som faktisk reflekterer databehandlingen beskrevet i denne specen
3. **Betaling:** Stripe (eller tilsvarende) aktivert, checkout → abonnement → kundeportal/webhook-flyt
4. **MVA/fakturering:** løsning tilpasset valgt betalingsflyt og kundens land
5. **Underleverandør-/DPA-oversikt:** alle tredjepartstjenester (hosting, e-post, betaling) kartlagt med databehandleravtale der relevant
6. **Kontrollplan-adskillelse:** verifiser i kode, ikke bare i dokumentasjon, at konto-/faktura-PII aldri kan nå intelligence-laget
7. **Domene/TLS:** offentlig domene, gyldig sertifikat, reverse proxy konfigurert
8. **Cookies/analytics:** ingen sporing/analytics/annonse-SDK som standard; eksplisitt, dokumentert beslutning hvis noe legges til senere
9. **Kildeattribusjon:** de frosne setningene i §2 faktisk rendret synlig på riktig sted i UI, ikke bare i et internt dokument
10. **Tilgjengelighet/sikkerhet:** grunnleggende tilgjengelighetstest, sikkerhetsheadere, autorisasjonstest (en bruker kan aldri se en annen brukers data), full checkout-ende-til-ende-test
11. **Corpus-boundary:** test bekrefter at anonym bruker ikke kan enumerere, hente eller rekonstruere hele opportunity-corpuset via ruter, API, sitemap, ID-sekvenser eller søk.

---

## 8. Teknisk arkitektur — føringer for webteamet

- Frontend konsumerer utelukkende `read_model.py`-kontrakten via et internt API-lag — aldri direkte databasetilgang
- Autentisering/kontodata i egen tabell/skjema, fysisk eller logisk adskilt fra intelligence-tabellene
- Ingen hemmeligheter (API-nøkler, databasepassord) i frontend-kode eller git-historikk
- CSV-eksport genereres server-side fra samme read model, ikke ved å eksponere et bredere internt API
- Offentlig demo/detail må bruke en eksplisitt public-record allowlist eller tilsvarende fail-closed mekanisme. Fravær fra denne listen betyr ikke offentlig tilgjengelig.
- Server/API må ikke tilby en anonym "list all", cursor/pagination, predictable-ID eller annen discovery-rute som omgår den betalte corpus-grensen.

---

## 9. Akseptansekriterier for denne fasen

1. En ny bruker kan registrere seg, sette opp en leverandørprofil, og umiddelbart se en relevant, ikke-tom feed basert på faktiske Lombardia-data
2. For enhver opportunity kan brukeren uten forklaring svare på: *Hva er dette? Hvorfor vises det? Hva kan det skape etterspørsel etter, og hvor er beviset? Hvordan passer det inn i markedet?*
3. Ingen av påstandene som er forbudt i §6 forekommer noe sted i kundevendt tekst — verifisert ved full gjennomlesning av nettstedet, ikke bare methodology-siden
4. Alle launch-portene i §7 er grønne før checkout aktiveres for reelle kunder
5. Standardeksempelet (demo, onboarding, markedsføring) viser ett demand-tag, med forbeholdet om sjeldenhet for flere
6. Kontosletting fjerner reelt all kundekontroll-PII; intelligence-laget verifiseres uendret av dette (det inneholder aldri kunde-PII i utgangspunktet)
7. Driftskostnad siste 30 dager er dokumentert og bekreftet under 400 kr/mnd-målet, betalingsgebyrer holdt separat
8. Repo-vidt kontaktsøk (samme metode som brukt gjennom hele prosjektet) viser fortsatt null treff på aktive kontaktveier
9. En autorisasjonstest bekrefter at bruker A aldri kan se bruker B sine lagrede muligheter eller kontodata
10. Navigasjonsstrukturen matcher §3 eksakt — ingen "Produktforklaring"-side med mindre Home er dokumentert utilstrekkelig, "dashboard" forekommer ikke som betegnelse på Opportunity Feed noe sted i UI eller kode, Supplier Profile og Account er separate sider
11. `/demo` viser ekte Lombardia-records med full customer-safe detail depth for det eksplisitt offentlige utvalget, korrekt attribusjonstekst rendret på selve siden uten at innlogging eller besøk på methodology kreves først
12. Repo-vidt tekstsøk (`grep -rn "CPV-blind" web/`) bekrefter at ingen intern terminologi har lekket inn i kundevendt kode eller kopi
13. Offentlig og betalt detail for samme public record serialiserer/render samme customer-safe evidensfelt og samme evidensinnhold; forskjellen ligger i corpus/workflow-tilgang, ikke detail depth
14. En anonym crawler-test kan ikke rekonstruere hele opportunity-corpuset gjennom offentlig sitemap, API, predictable IDs, søk eller paginering
15. Pricing/Home/Demo bruker ikke "Unlock full evidence" eller tilsvarende paywall-språk for offentlig viste records; CTA selger matching, breadth og løpende arbeidsflyt
16. Varsling/alerts forekommer ikke som inkludert launch-funksjon eller pricing-argument før funksjonen faktisk er implementert, testet og godkjent

---

## 10. Eksplisitt ikke-mål for denne fasen

- Ingen ny datakildeutvidelse (Puglia, Campania, andre regioner) er en forutsetning for å fullføre webfasen — dette er en parallell, uavhengig arbeidsstrøm
- Ingen AI-basert relevans-scoring eller sannsynlighetstall skal introduseres — relevansmodellen i §5 er endelig for denne versjonen
- Ingen flerspråklig UI utover italiensk/engelsk er nødvendig ved lansering
- Ingen alert-/notification-funksjon er nødvendig ved launch; den kan bare bli en betalt funksjon etter egen implementasjon og godkjenning